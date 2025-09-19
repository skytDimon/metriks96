#!/bin/bash

# Скрипт для исправления прав доступа к файлам на сервере
# Этот скрипт нужно запустить на сервере для исправления проблем с админ панелью

echo "Исправление прав доступа к файлам..."

# Получаем путь к директории проекта
PROJECT_DIR=$(dirname "$(readlink -f "$0")")

echo "Директория проекта: $PROJECT_DIR"

# Исправляем права доступа к файлам данных
echo "Исправление прав доступа к hidden_products.json..."
chmod 664 "$PROJECT_DIR/hidden_products.json"

echo "Исправление прав доступа к CSV файлу..."
chmod 664 "$PROJECT_DIR/store-7407308-202509021623.csv"

echo "Исправление прав доступа к orders.json..."
if [ -f "$PROJECT_DIR/orders.json" ]; then
    chmod 664 "$PROJECT_DIR/orders.json"
else
    echo "Файл orders.json не найден, создаем его..."
    echo '[]' > "$PROJECT_DIR/orders.json"
    chmod 664 "$PROJECT_DIR/orders.json"
fi

echo "Исправление прав доступа к settings.json..."
if [ -f "$PROJECT_DIR/settings.json" ]; then
    chmod 664 "$PROJECT_DIR/settings.json"
else
    echo "Файл settings.json не найден, создаем его..."
    echo '{}' > "$PROJECT_DIR/settings.json"
    chmod 664 "$PROJECT_DIR/settings.json"
fi

# Устанавливаем владельца файлов (замените www-data на пользователя веб-сервера)
echo "Установка владельца файлов..."
if [ -n "$1" ]; then
    USER="$1"
else
    USER="metriks66"
fi

echo "Установка владельца: $USER"
chown $USER:$USER "$PROJECT_DIR/hidden_products.json"
chown $USER:$USER "$PROJECT_DIR/store-7407308-202509021623.csv"

if [ -f "$PROJECT_DIR/orders.json" ]; then
    chown $USER:$USER "$PROJECT_DIR/orders.json"
fi

if [ -f "$PROJECT_DIR/settings.json" ]; then
    chown $USER:$USER "$PROJECT_DIR/settings.json"
fi

echo "Проверка прав доступа:"
ls -la "$PROJECT_DIR/hidden_products.json"
ls -la "$PROJECT_DIR/store-7407308-202509021623.csv"
if [ -f "$PROJECT_DIR/orders.json" ]; then
    ls -la "$PROJECT_DIR/orders.json"
fi
if [ -f "$PROJECT_DIR/settings.json" ]; then
    ls -la "$PROJECT_DIR/settings.json"
fi

echo "Готово! Права доступа исправлены."
echo ""
echo "Если проблемы остаются, проверьте:"
echo "1. Запущен ли веб-сервер под правильным пользователем"
echo "2. Есть ли права на запись в директорию проекта"
echo "3. Правильно ли настроен SELinux (если используется)"
