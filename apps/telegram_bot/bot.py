import os
import django
from telegram.ext import Application
from dotenv import load_dotenv

# Загрузка переменных окружения должна быть до настройки Django
load_dotenv()

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Импорт обработчиков после настройки Django
from .handlers import setup_handlers


def main() -> None:
    """Запуск Telegram бота"""

    # Токен бота из переменных окружения
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not bot_token:
        print("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return

    # Создаем приложение
    application = Application.builder().token(bot_token).build()

    # Настраиваем обработчики
    setup_handlers(application)

    print("Telegram бот запускается...")
    print(f"Токен: {bot_token[:10]}...")

    # Запускаем бота
    application.run_polling(allowed_updates=None)


if __name__ == '__main__':
    main()
