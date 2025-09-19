#!/bin/bash

# Скрипт для исправления прав доступа к файлам проекта

echo "🔧 Исправляем права доступа к файлам..."

# Проверяем, запущен ли скрипт от root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Для исправления прав доступа нужны права root"
    echo "Запустите: sudo ./fix_permissions.sh"
    exit 1
fi

# Устанавливаем правильные права для файлов данных
echo "📁 Устанавливаем права для файлов данных..."

# Создаем файл hidden_products.json если его нет
if [ ! -f "hidden_products.json" ]; then
    echo "📝 Создаем файл hidden_products.json..."
    echo '{"hidden_products": []}' > hidden_products.json
fi

# Создаем файл orders.json если его нет
if [ ! -f "orders.json" ]; then
    echo "📝 Создаем файл orders.json..."
    echo '[]' > orders.json
fi

# Устанавливаем права доступа
chmod 664 hidden_products.json
chmod 664 orders.json
chmod 664 store-7407308-202509021623.csv

# Устанавливаем владельца (замените 'www-data' на пользователя, под которым запускается приложение)
if id "www-data" &>/dev/null; then
    chown www-data:www-data hidden_products.json
    chown www-data:www-data orders.json
    chown www-data:www-data store-7407308-202509021623.csv
    echo "✅ Права установлены для пользователя www-data"
elif id "nginx" &>/dev/null; then
    chown nginx:nginx hidden_products.json
    chown nginx:nginx orders.json
    chown nginx:nginx store-7407308-202509021623.csv
    echo "✅ Права установлены для пользователя nginx"
else
    echo "⚠️  Пользователи www-data и nginx не найдены"
    echo "Установите владельца вручную:"
    echo "chown USER:GROUP hidden_products.json orders.json store-7407308-202509021623.csv"
fi

# Проверяем права доступа
echo "🔍 Проверяем права доступа:"
ls -la hidden_products.json orders.json store-7407308-202509021623.csv

echo "✅ Права доступа исправлены!"
echo ""
echo "📋 Если проблема остается, проверьте:"
echo "1. Под каким пользователем запускается приложение"
echo "2. Логи приложения: docker-compose logs -f или journalctl -u metriks -f"
echo "3. Права на директорию проекта"
