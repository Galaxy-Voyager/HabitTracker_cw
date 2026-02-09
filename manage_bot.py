#!/usr/bin/env python
"""Скрипт для запуска Telegram бота"""
import os
import sys

# Добавляем проект в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from apps.telegram_bot.bot import main
    main()
