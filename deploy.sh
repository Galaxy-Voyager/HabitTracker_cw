#!/bin/bash

# deploy.sh - скрипт для деплоя на сервере

set -e

echo "=== Habit Tracker Deployment Script ==="
echo "Start time: $(date)"

# Переходим в директорию проекта
cd ~/habittracker || { echo "Directory ~/habittracker not found!"; exit 1; }

# Обновляем код из репозитория
echo "Updating code from repository..."
git pull origin main

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    if [ -f env.example.txt ]; then
        cp env.example.txt .env
        echo "⚠️  Please update .env file with your actual values!"
        echo "⚠️  Run: nano .env"
    else
        echo "❌ env.example.txt not found!"
        exit 1
    fi
fi

# Останавливаем контейнеры
echo "Stopping containers..."
docker compose down

# Пересобираем и запускаем
echo "Building and starting containers..."
docker compose up -d --build

# Проверяем статус контейнеров
echo "Checking container status..."
sleep 5
docker compose ps

# Проверяем, что веб-сервер отвечает
echo "Checking web server response..."
curl -f http://localhost/api/public/ || echo "⚠️  Web server not responding yet"

# Очищаем неиспользуемые образы
echo "Cleaning up old images..."
docker system prune -f

echo "=== Deployment completed successfully! ==="
echo "Application should be available at:"
echo "  - http://158.160.3.59"
echo "  - http://158.160.3.59/admin/"
echo "Finish time: $(date)"
