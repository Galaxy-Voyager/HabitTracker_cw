#!/bin/bash

# deploy.sh - универсальный скрипт деплоя

set -e

echo "=== Habit Tracker Deployment Script ==="
echo "Start time: $(date)"

# Функция для установки Docker
install_docker() {
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo usermod -aG docker $USER
    echo "Docker installed. Please log out and back in."
}

# Функция для установки Docker Compose
install_docker_compose() {
    echo "Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
}

# Проверка и установка Docker
if ! command -v docker &> /dev/null; then
    install_docker
else
    echo "✅ Docker already installed"
fi

# Проверка Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    install_docker_compose
else
    echo "✅ Docker Compose already installed"
fi

# Переходим в директорию проекта
cd ~/habittracker || { 
    echo "Creating project directory..."
    mkdir -p ~/habittracker
    cd ~/habittracker
}

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ .env file not found! Creating from template..."
    if [ -f .env.production.example ]; then
        cp .env.production.example .env
        echo "⚠️  Please edit .env file with your values!"
        echo "Run: nano .env"
        exit 1
    else
        echo "❌ No .env template found!"
        exit 1
    fi
fi

# Останавливаем старые контейнеры
echo "Stopping old containers..."
docker compose down || true

# Запускаем новые контейнеры
echo "Starting new containers..."
docker compose up -d --build

# Ждем запуска
sleep 10

# Применяем миграции
echo "Applying migrations..."
docker compose exec -T web python manage.py migrate

# Проверяем статус
echo "Container status:"
docker compose ps

# Проверяем работоспособность
echo "Testing API..."
curl -f http://localhost/api/public/ || echo "⚠️  API not responding yet"

echo "=== Deployment completed! ==="
echo "Application: http://$(curl -s ifconfig.me)/"
