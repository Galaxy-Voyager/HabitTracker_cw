#!/bin/bash
set -e

echo "=== Habit Tracker Deployment Script ==="
echo "Start time: $(date)"

# Получаем параметры
SECRET_KEY=$1
TELEGRAM_BOT_TOKEN=$2
SERVER_IP=$3

echo "Parameters received:"
echo "SERVER_IP: $SERVER_IP"
echo "TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "SECRET_KEY: ${SECRET_KEY:0:10}..."

# Создаём директорию проекта
mkdir -p ~/habittracker
cd ~/habittracker

# Копируем файлы проекта (если они ещё не скопированы)
# В этом скрипте мы предполагаем, что файлы уже скопированы через SCP

# Установка Docker если не установлен
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo usermod -aG docker $USER
    echo "Docker installed"
else
    echo "✅ Docker already installed"
fi

# Установка Docker Compose если не установлен
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
    echo "Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Создание .env файла
echo "Creating .env file..."
cat > .env << EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
DATABASE_URL=postgresql://habittracker_user:habittracker_password@postgres:5432/habittracker_db
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
POSTGRES_USER=habittracker_user
POSTGRES_PASSWORD=habittracker_password
POSTGRES_DB=habittracker_db
EOF

echo ".env file created:"
cat .env | grep -v PASSWORD | grep -v TOKEN | grep -v KEY

# Останавливаем старые контейнеры
echo "Stopping old containers..."
docker compose down || true

# Запускаем новые контейнеры
echo "Starting new containers..."
docker compose up -d --build

# Ждем запуска
echo "Waiting for containers to start..."
sleep 10

# Применяем миграции
echo "Applying migrations..."
docker compose exec -T web python manage.py migrate

# Проверяем статус
echo "Container status:"
docker compose ps

# Проверяем работоспособность
echo "Testing API..."
curl -f http://localhost/api/public/ && echo "✅ API is responding" || echo "⚠️ API not responding yet"

echo "=== Deployment completed! ==="
echo "Application: http://$SERVER_IP"
