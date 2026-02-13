import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from django.contrib.auth import get_user_model
from apps.habits.models import Habit
from datetime import datetime
from asgiref.sync import sync_to_async

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
PLACE, TIME, ACTION, DURATION, PERIODICITY, REWARD, CONFIRM = range(7)

User = get_user_model()


# Асинхронные обертки для Django ORM
@sync_to_async
def get_user_by_chat_id(chat_id):
    """Получить пользователя по chat_id"""
    return User.objects.filter(telegram_chat_id=chat_id).first()


@sync_to_async
def create_user(username, chat_id, password):
    """Создать нового пользователя"""
    return User.objects.create_user(
        username=username,
        telegram_chat_id=chat_id,
        password=password
    )


@sync_to_async
def get_user_habits(user):
    """Получить привычки пользователя"""
    return list(Habit.objects.filter(user=user).order_by('time')[:10])


@sync_to_async
def create_habit(user, place, habit_time, action, execution_time,
                 periodicity, reward):
    """Создать новую привычку"""
    return Habit.objects.create(
        user=user,
        place=place,
        time=habit_time,
        action=action,
        execution_time=execution_time,
        periodicity=periodicity,
        reward=reward,
        is_public=False
    )


@sync_to_async
def get_public_habits_with_usernames():
    """Получить публичные привычки с именами пользователей"""
    habits = Habit.objects.filter(is_public=True).order_by('-created_at')[:5]
    result = []
    for habit in habits:
        result.append({
            'action': habit.action,
            'username': habit.user.username,
            'time': habit.time,
            'place': habit.place,
            'execution_time': habit.execution_time,
            'periodicity': habit.periodicity
        })
    return result


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    chat_id = str(update.effective_chat.id)

    try:
        # Ищем пользователя по Telegram Chat ID
        django_user = await get_user_by_chat_id(chat_id)

        if not django_user:
            # Создаем нового пользователя если не найден
            username = f"telegram_{user.username or user.id}"
            django_user = await create_user(
                username, chat_id, os.urandom(16).hex()
            )
            message = (
                f"Привет, {user.first_name}!\n"
                f"Вы зарегистрированы в Habit Tracker!\n"
                f"Ваш логин: {username}\n\n"
                f"Доступные команды:\n"
                f"/create - Создать привычку\n"
                f"/myhabits - Мои привычки\n"
                f"/public - Публичные привычки\n"
                f"/help - Помощь"
            )
        else:
            message = (
                f"С возвращением, {django_user.username}!\n\n"
                f"Доступные команды:\n"
                f"/create - Создать привычку\n"
                f"/myhabits - Мои привычки\n"
                f"/public - Публичные привычки\n"
                f"/help - Помощь"
            )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def create_habit_start(update: Update,
                             context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало создания привычки"""
    chat_id = str(update.effective_chat.id)

    # Проверяем, зарегистрирован ли пользователь
    user = await get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text(
            "Вы не зарегистрированы. Используйте /start для регистрации."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Создание новой привычки\n\n"
        "Введите место, где будете выполнять привычку:\n"
        "Например: Дома, В парке, На работе"
    )

    return PLACE


async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем место"""
    context.user_data['place'] = update.message.text

    await update.message.reply_text(
        "Введите время выполнения (формат ЧЧ:ММ):\n"
        "Например: 09:00, 18:30"
    )

    return TIME


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем время"""
    try:
        # Парсим время
        time_str = update.message.text
        habit_time = datetime.strptime(time_str, '%H:%M').time()
        context.user_data['time'] = habit_time

        await update.message.reply_text(
            "Введите действие (что будете делать):\n"
            "Например: Читать книгу, Делать зарядку, Медитировать"
        )

        return ACTION

    except ValueError:
        await update.message.reply_text(
            "Неверный формат времени. Используйте ЧЧ:ММ\n"
            "Попробуйте еще раз:"
        )
        return TIME


async def get_action(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем действие"""
    context.user_data['action'] = update.message.text

    keyboard = [['60', '90', '120']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Введите время на выполнение в секундах (максимум 120):",
        reply_markup=reply_markup
    )

    return DURATION


async def get_duration(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем продолжительность"""
    try:
        duration = int(update.message.text)
        if duration > 120:
            await update.message.reply_text(
                "Время выполнения не должно превышать 120 секунд.\n"
                "Введите снова:"
            )
            return DURATION

        context.user_data['execution_time'] = duration

        keyboard = [['Ежедневно', 'Еженедельно']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await update.message.reply_text(
            "Выберите периодичность:",
            reply_markup=reply_markup
        )

        return PERIODICITY

    except ValueError:
        await update.message.reply_text(
            "Введите число (секунды):"
        )
        return DURATION


async def get_periodicity(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем периодичность"""
    periodicity_text = update.message.text

    if periodicity_text == 'Ежедневно':
        context.user_data['periodicity'] = 'daily'
        context.user_data['day_of_week'] = None
        await update.message.reply_text(
            "Введите вознаграждение (или 'нет' если не нужно):\n"
            "Например: Чашка кофе, Просмотр сериала, Сладость"
        )
        return REWARD
    else:
        context.user_data['periodicity'] = 'weekly'
        # Для еженедельных нужно будет спросить день недели
        keyboard = [
            ['Понедельник', 'Вторник', 'Среда'],
            ['Четверг', 'Пятница', 'Суббота'],
            ['Воскресенье']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await update.message.reply_text(
            "Выберите день недели:",
            reply_markup=reply_markup
        )

        # Пропускаем REWARD для еженедельных
        context.user_data['skip_reward'] = True
        return REWARD


async def get_reward(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем вознаграждение"""
    # Проверяем, нужно ли спрашивать день недели
    if context.user_data.get('periodicity') == 'weekly' and 'day_of_week' not in context.user_data:
        day_map = {
            'Понедельник': 1, 'Вторник': 2, 'Среда': 3,
            'Четверг': 4, 'Пятница': 5, 'Суббота': 6, 'Воскресенье': 7
        }
        context.user_data['day_of_week'] = day_map.get(update.message.text)
        await update.message.reply_text(
            "Введите вознаграждение (или 'нет' если не нужно):\n"
            "Например: Чашка кофе, Просмотр сериала, Сладость"
        )
        return REWARD

    reward = update.message.text
    if reward.lower() == 'нет':
        context.user_data['reward'] = ''
    else:
        context.user_data['reward'] = reward

    # Подтверждение
    place = context.user_data.get('place', '')
    habit_time = context.user_data.get('time', '')
    action = context.user_data.get('action', '')
    execution_time = context.user_data.get('execution_time', 0)
    periodicity = context.user_data.get('periodicity', '')
    reward_text = context.user_data.get('reward', 'нет')

    periodicity_text = 'ежедневно' if periodicity == 'daily' else 'еженедельно'

    summary = (
        f"ПОДТВЕРЖДЕНИЕ ПРИВЫЧКИ:\n\n"
        f"Место: {place}\n"
        f"Время: {habit_time}\n"
        f"Действие: {action}\n"
        f"Длительность: {execution_time} сек.\n"
        f"Периодичность: {periodicity_text}\n"
        f"Вознаграждение: {reward_text}\n\n"
        f"Все верно? (да/нет)"
    )

    keyboard = [['Да', 'Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        summary,
        reply_markup=reply_markup
    )

    return CONFIRM


async def confirm_habit(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждение и создание привычки"""
    response = update.message.text.lower()

    if response == 'да':
        chat_id = str(update.effective_chat.id)
        user = await get_user_by_chat_id(chat_id)

        try:
            # Создаем привычку
            habit = await create_habit(
                user=user,
                place=context.user_data['place'],
                habit_time=context.user_data['time'],
                action=context.user_data['action'],
                execution_time=context.user_data['execution_time'],
                periodicity=context.user_data['periodicity'],
                reward=context.user_data.get('reward', '')
            )

            # Преобразуем периодичность для читаемости
            periodicity_text = (
                'ежедневно' if habit.periodicity == 'daily'
                else 'еженедельно'
            )

            await update.message.reply_text(
                f"Привычка создана успешно!\n\n"
                f"ID привычки: {habit.id}\n"
                f"{habit.action}\n"
                f"в {habit.time} в {habit.place}\n"
                f"{periodicity_text}\n\n"
                f"Вы получите напоминание в указанное время!",
                reply_markup=ReplyKeyboardRemove()
            )

        except Exception as e:
            logger.error(f"Error creating habit: {e}")
            await update.message.reply_text(
                f"Ошибка при создании привычки: {str(e)}",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        await update.message.reply_text(
            "Создание привычки отменено.",
            reply_markup=ReplyKeyboardRemove()
        )

    # Очищаем данные
    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена создания привычки"""
    await update.message.reply_text(
        "Создание привычки отменено.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


async def my_habits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать мои привычки"""
    chat_id = str(update.effective_chat.id)

    try:
        user = await get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "Вы не зарегистрированы. Используйте /start"
            )
            return

        habits = await get_user_habits(user)

        if not habits:
            await update.message.reply_text(
                "У вас пока нет привычек. "
                "Используйте /create чтобы создать первую!"
            )
            return

        message = "ВАШИ ПРИВЫЧКИ:\n\n"

        for i, habit in enumerate(habits, 1):
            periodicity = (
                'ежедневно' if habit.periodicity == 'daily'
                else 'еженедельно'
            )
            reward = f"\n   Вознаграждение: {habit.reward}" if habit.reward else ""

            message += (
                f"{i}. {habit.action}\n"
                f"   {habit.time} в {habit.place}\n"
                f"   {habit.execution_time} сек. | {periodicity}{reward}\n\n"
            )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error in my_habits: {e}")
        await update.message.reply_text("Произошла ошибка.")


async def public_habits(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать публичные привычки"""
    try:
        habits = await get_public_habits_with_usernames()

        if not habits:
            await update.message.reply_text("Публичных привычек пока нет.")
            return

        message = "ПУБЛИЧНЫЕ ПРИВЫЧКИ:\n\n"

        for i, habit in enumerate(habits, 1):
            periodicity = (
                'ежедневно' if habit['periodicity'] == 'daily'
                else 'еженедельно'
            )

            message += (
                f"{i}. {habit['action']}\n"
                f"   {habit['username']}\n"
                f"   {habit['time']} в {habit['place']}\n"
                f"   {habit['execution_time']} сек. | {periodicity}\n\n"
            )

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error in public_habits: {e}")
        await update.message.reply_text("Произошла ошибка.")


async def help_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    """Помощь"""
    help_text = (
        "HABIT TRACKER BOT - ПОМОЩЬ\n\n"
        "Доступные команды:\n"
        "/start - Начать работу и зарегистрироваться\n"
        "/create - Создать новую привычку\n"
        "/myhabits - Показать мои привычки\n"
        "/public - Показать публичные привычки\n"
        "/help - Эта справка\n\n"
        "Пример создания привычки:\n"
        "1. /create\n"
        "2. Введите место\n"
        "3. Введите время (ЧЧ:ММ)\n"
        "4. Введите действие\n"
        "5. Выберите периодичность\n"
        "6. Укажите вознаграждение\n\n"
        "Бот будет отправлять напоминания!"
    )

    await update.message.reply_text(help_text)


def setup_handlers(application: Application) -> None:
    """Настройка обработчиков команд"""

    # Conversation Handler для создания привычки
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create_habit_start)],
        states={
            PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_place)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_action)],
            DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)
            ],
            PERIODICITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_periodicity)
            ],
            REWARD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_reward)
            ],
            CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_habit)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Регистрация обработчиков
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('myhabits', my_habits))
    application.add_handler(CommandHandler('public', public_habits))
    application.add_handler(CommandHandler('help', help_command))
