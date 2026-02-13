#!/bin/bash
set -e

echo "=== Habit Tracker Deployment Script ==="
echo "Start time: $(date)"

# ???????? ?????????
SECRET_KEY=$1
TELEGRAM_BOT_TOKEN=$2
SERVER_IP=$3

echo "Parameters received:"
echo "SERVER_IP: $SERVER_IP"
echo "TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "SECRET_KEY: ${SECRET_KEY:0:10}..."

mkdir -p ~/habittracker
cd ~/habittracker

if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
else
    echo "? Docker already installed"
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-v2 || true

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "Trying alternative installation method..."
        sudo apt-get install -y ca-certificates curl
        sudo install -m 0755 -d /etc/apt/keyrings
        sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-compose-plugin
    fi
else
    echo "? Docker Compose already installed"
fi

echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker compose version || echo "not available")"

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

docker compose down || true
docker compose up -d --build
sleep 10
docker compose exec -T web python manage.py migrate
docker compose ps
curl -f http://localhost/api/public/ && echo "? API is responding" || echo "?? API not responding yet"

echo "=== Deployment completed! ==="
echo "Application: http://$SERVER_IP"
