#!/bin/bash

# Скрипт деплоя для продакшна
set -e

echo "🚀 Начинаем деплой МЕТРИКС..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Скопируйте env.example в .env и заполните настройки:"
    echo "   cp env.example .env"
    echo "   nano .env"
    exit 1
fi

# Проверяем наличие CSV файла
if [ ! -f "store-7407308-202509021623.csv" ]; then
    echo "❌ CSV файл с товарами не найден!"
    echo "📁 Убедитесь, что файл store-7407308-202509021623.csv находится в корне проекта"
    exit 1
fi

# Создаем необходимые директории
echo "📁 Создаем директории..."
mkdir -p logs
mkdir -p /var/log/metriks 2>/dev/null || echo "⚠️  Не удалось создать /var/log/metriks (нужны права root)"

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
if [ -d "env" ]; then
    source env/bin/activate
    pip install -r requirements.txt
else
    echo "❌ Виртуальное окружение не найдено!"
    echo "🔧 Создайте виртуальное окружение:"
    echo "   python -m venv env"
    echo "   source env/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Проверяем конфигурацию
echo "🔍 Проверяем конфигурацию..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_IDS', 
    'SMTP_PASSWORD'
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f'❌ Отсутствуют переменные окружения: {missing_vars}')
    exit(1)
else:
    print('✅ Все необходимые переменные окружения настроены')
"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка конфигурации!"
    exit 1
fi

# Тестируем приложение
echo "🧪 Тестируем приложение..."
python -c "
from app.main import app
from app.telegram_service import TELEGRAM_SERVICE
print('✅ Приложение загружается корректно')
if TELEGRAM_SERVICE:
    print('✅ Telegram сервис настроен')
else:
    print('⚠️  Telegram сервис не настроен')
"

# Запускаем приложение
echo "🎯 Выберите способ запуска:"
echo "1) Docker Compose (рекомендуется)"
echo "2) Systemd service"
echo "3) Gunicorn напрямую"
echo "4) Uvicorn для разработки"

read -p "Введите номер (1-4): " choice

case $choice in
    1)
        echo "🐳 Запускаем через Docker Compose..."
        docker compose up -d
        echo "✅ Приложение запущено через Docker Compose"
        echo "🌐 Доступно по адресу: http://localhost"
        ;;
    2)
        echo "⚙️  Настраиваем systemd service..."
        sudo cp metriks.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable metriks
        sudo systemctl start metriks
        echo "✅ Приложение запущено как systemd service"
        echo "📊 Статус: sudo systemctl status metriks"
        ;;
    3)
        echo "🚀 Запускаем через Gunicorn..."
        gunicorn -c gunicorn.conf.py app.main:app
        ;;
    4)
        echo "🔧 Запускаем через Uvicorn (для разработки)..."
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo "🎉 Деплой завершен!"
echo "📋 Полезные команды:"
echo "   - Логи: docker-compose logs -f (для Docker)"
echo "   - Логи: sudo journalctl -u metriks -f (для systemd)"
echo "   - Остановка: docker-compose down (для Docker)"
echo "   - Остановка: sudo systemctl stop metriks (для systemd)"
