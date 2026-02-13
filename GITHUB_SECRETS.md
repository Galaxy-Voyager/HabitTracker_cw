# Настройка GitHub Secrets для Habit Tracker

## Необходимые секреты:

1. **SSH_PRIVATE_KEY** - приватный SSH ключ для доступа к серверу
2. **SERVER_IP** - IP адрес сервера (158.160.3.59)
3. **SERVER_USER** - пользователь на сервере (voyager1)
4. **TELEGRAM_BOT_TOKEN** - токен вашего Telegram бота
5. **SECRET_KEY** - секретный ключ Django для продакшена

## Инструкция по добавлению:

1. Перейдите в репозиторий на GitHub: https://github.com/yourusername/HabitTracker_cw
2. Нажмите Settings → Secrets and variables → Actions
3. Нажмите "New repository secret"

### Создание SSH ключа для GitHub Actions (если еще нет):

В PowerShell (локально):
ssh-keygen -t rsa -b 4096 -f C:\Users\RubyDiamond\.ssh\github_actions -C "github-actions@habittracker"

### Добавление ключа на сервер:

Подключитесь к серверу:
ssh voyager1@158.160.3.59

Добавьте публичный ключ:
echo "ssh-rsa AAAAB3... ваш_публичный_ключ ... github-actions@habittracker" >> ~/.ssh/authorized_keys

Проверьте права:
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

### Добавление секретов в GitHub:

| Secret Name | Value |
|------------|-------|
| SSH_PRIVATE_KEY | Содержимое файла C:\Users\RubyDiamond\.ssh\github_actions (весь текст, включая BEGIN и END) |
| SERVER_IP | 158.160.3.59 |
| SERVER_USER | voyager1 |
| TELEGRAM_BOT_TOKEN | Ваш токен от @BotFather |
| SECRET_KEY | Сгенерируйте новый ключ (см. ниже) |

### Генерация SECRET_KEY:

Запустите Python и выполните:
import secrets
print(secrets.token_urlsafe(50))

## Проверка настроек:

После добавления всех секретов, сделайте коммит и пуш в ветку main:

git add .
git commit -m "Add CI/CD configuration"
git push origin main

Затем проверьте вкладку Actions в репозитории - должен запуститься workflow.
