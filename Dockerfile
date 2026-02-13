# Базовый образ
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .
COPY requirements-dev.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn==21.2.0

# Копирование проекта
COPY . .

# Создание директории для статических файлов
RUN mkdir -p /app/staticfiles

# Сбор статических файлов (будет выполнено при запуске)
RUN python manage.py collectstatic --noinput

# Открытие порта
EXPOSE 8000

# Команда для запуска Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
