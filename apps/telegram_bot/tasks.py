import os
import requests
from celery import shared_task
from apps.habits.models import Habit


@shared_task
def send_telegram_reminder(habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user

        if not user.telegram_chat_id:
            print(f"User {user.username} has no Telegram chat ID")
            return

        message = f"🔔 Напоминание о привычке!\n\n" \
                  f"Привычка: {habit.action}\n" \
                  f"Время: {habit.time}\n" \
                  f"Место: {habit.place}\n" \
                  f"Время на выполнение: {habit.execution_time} сек."

        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("TELEGRAM_BOT_TOKEN not set")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': user.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")

    except Habit.DoesNotExist:
        print(f"Habit with id {habit_id} does not exist")
    except Exception as e:
        print(f"Error sending reminder: {e}")


@shared_task
def check_and_send_reminders():
    from django.utils import timezone

    now = timezone.now()
    current_time = now.time()
    current_weekday = now.weekday() + 1

    habits = Habit.objects.all()

    for habit in habits:
        if not habit.user.telegram_chat_id:
            continue

        habit_time = habit.time

        if habit.periodicity == 'daily':
            time_diff = abs(
                (current_time.hour * 60 + current_time.minute) -
                (habit_time.hour * 60 + habit_time.minute)
            )
            if time_diff <= 5:
                send_telegram_reminder.delay(habit.id)

        elif habit.periodicity == 'weekly' and habit.day_of_week:
            if habit.day_of_week == current_weekday:
                time_diff = abs(
                    (current_time.hour * 60 + current_time.minute) -
                    (habit_time.hour * 60 + habit_time.minute)
                )
                if time_diff <= 5:
                    send_telegram_reminder.delay(habit.id)
