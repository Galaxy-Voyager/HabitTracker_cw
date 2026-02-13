#!/bin/bash
set -e

echo "=== Starting deployment ==="
cd ~/habittracker

# Установка Docker если нужно
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo usermod -aG docker $USER
fi

# Установка Docker Compose если нужно
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
fi

# Создание .env файла
echo "Creating .env file..."
cat > .env << EOF
DEBUG=False
SECRET_KEY=$1
DATABASE_URL=postgresql://habittracker_user:habittracker_password@postgres:5432/habittracker_db
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=$2
ALLOWED_HOSTS=localhost,127.0.0.1,$3
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
POSTGRES_USER=habittracker_user
POSTGRES_PASSWORD=habittracker_password
POSTGRES_DB=habittracker_db
EOF

# Запуск контейнеров
docker compose down || true
docker compose up -d --build
sleep 10
docker compose exec -T web python manage.py migrate
docker system prune -f

echo "=== Deployment complete ==="
