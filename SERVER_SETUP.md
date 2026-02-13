# Инструкция по настройке сервера для Habit Tracker

## 1. Подключение к серверу

ssh voyager1@158.160.3.59

## 2. Установка Docker и Docker Compose

sudo apt update && sudo apt upgrade -y

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo usermod -aG docker $USER

sudo apt-get install -y docker-compose-plugin

## 3. Проверка установки

docker --version
docker compose version

## 4. Настройка firewall (уже выполнено)

sudo ufw status
# Должны быть открыты порты: 22, 80, 443

## 5. Выход и повторный вход для применения группы docker

exit

## 6. Снова подключитесь и проверьте группу

ssh voyager1@158.160.3.59
groups
# В списке должно быть docker

## 7. Создание структуры директорий

mkdir -p ~/habittracker
cd ~/habittracker

## 8. Клонирование репозитория (для первого деплоя)

git clone https://github.com/yourusername/HabitTracker_cw.git .
# или если уже есть файлы:
git init
git remote add origin https://github.com/yourusername/HabitTracker_cw.git
git pull origin main

## 9. Создание .env файла

cp .env.production.example .env
nano .env
# Заполните все переменные:
# - SECRET_KEY: сгенерируйте новый
# - TELEGRAM_BOT_TOKEN: ваш токен

## 10. Проверка конфигурации

docker compose config

## 11. Запуск вручную (для теста)

docker compose up -d --build

## 12. Проверка статуса

docker compose ps
docker compose logs web

## 13. Проверка доступности приложения

curl http://localhost/api/public/
# Должен вернуться JSON ответ

## 14. Настройка автоматического деплоя

Убедитесь, что в GitHub добавлены секреты:
- SSH_PRIVATE_KEY
- SERVER_IP (158.160.3.59)
- SERVER_USER (voyager1)
- TELEGRAM_BOT_TOKEN
- SECRET_KEY

## 15. Полезные команды

# Просмотр логов
docker compose logs -f web
docker compose logs -f celery_worker
docker compose logs -f nginx

# Перезапуск конкретного сервиса
docker compose restart web

# Остановка всех контейнеров
docker compose down

# Пересборка и запуск
docker compose up -d --build

# Очистка неиспользуемых образов
docker system prune -f
