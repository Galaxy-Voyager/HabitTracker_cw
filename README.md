# Habit Tracker - Курсовая работа

Трекер полезных привычек на основе книги "Атомные привычки" Джеймса Клира.

## Функциональность

- Регистрация и аутентификация пользователей (JWT)
- CRUD операции для привычек
- Валидация привычек согласно бизнес-правилам
- Публичные привычки для общего доступа
- Пагинация списков (по 5 привычек на страницу)
- Интеграция с Telegram для напоминаний
- Отложенные задачи через Celery + Redis
- CORS настройки для фронтенда

## Установка и запуск

### 1. Клонирование и настройка

\`\`\`
git clone <repository-url>
cd HabitTracker_cw
\`\`\`

### 2. Установка зависимостей

\`\`\`
poetry install
\`\`\`

### 3. Настройка переменных окружения

Создайте файл \`.env\` в корне проекта:

\`\`\`
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
\`\`\`

### 4. Запуск Redis

\`\`\`
docker run -d -p 6379:6379 redis
\`\`\`

### 5. Применение миграций

\`\`\`
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 6. Создание суперпользователя

\`\`\`
python manage.py createsuperuser
\`\`\`

### 7. Запуск сервера разработки

\`\`\`
python manage.py runserver
\`\`\`

### 8. Запуск Celery worker

\`\`\`
celery -A config worker -l info
\`\`\`

### 9. Запуск Celery beat (для периодических задач)

\`\`\`
celery -A config beat -l info
\`\`\`

## API Endpoints

### Аутентификация
- \`POST /api/auth/register/\` - Регистрация пользователя
- \`POST /api/auth/token/\` - Получение JWT токена
- \`POST /api/auth/token/refresh/\` - Обновление токена

### Привычки
- \`GET /api/habits/\` - Список привычек текущего пользователя
- \`POST /api/habits/\` - Создание новой привычки
- \`GET /api/habits/{id}/\` - Получение конкретной привычки
- \`PUT /api/habits/{id}/\` - Обновление привычки
- \`PATCH /api/habits/{id}/\` - Частичное обновление привычки
- \`DELETE /api/habits/{id}/\` - Удаление привычки
- \`POST /api/habits/{id}/complete/\` - Отметить привычку как выполненную
- \`GET /api/public/\` - Список публичных привычек (доступно без аутентификации)

## Валидация привычек

1. **Нельзя одновременно указывать и связанную привычку, и вознаграждение**
2. **Время выполнения не должно превышать 120 секунд**
3. **В связанные привычки могут попадать только приятные привычки**
4. **У приятной привычки не может быть вознаграждения или связанной привычки**
5. **Для еженедельных привычек необходимо указать день недели**

## Интеграция с Telegram

### Настройка бота:

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Добавьте токен в переменную окружения \`TELEGRAM_BOT_TOKEN\`
4. Пользователь должен указать свой Telegram Chat ID в профиле

## Тестирование

\`\`\`
# Запуск всех тестов
python manage.py test

# Запуск тестов с покрытием
pytest --cov=apps

# Проверка стиля кода
flake8 apps/
\`\`\`

## Технологии

- Python 3.11+
- Django 5.0+
- Django REST Framework
- JWT аутентификация (djangorestframework-simplejwt)
- Celery + Redis для отложенных задач
- Django Filter для фильтрации
- PostgreSQL
- Telegram Bot API
- Pytest для тестирования
- Flake8 для проверки стиля кода