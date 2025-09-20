#!/bin/bash

# Скрипт для исправления прав доступа к файлам на сервере metriks96.ru
# IP: 45.144.64.68
# Пользователь: metriks66
# ОС: Ubuntu-24.04-amd64

echo "=========================================="
echo "Исправление прав доступа для metriks96.ru"
echo "=========================================="

# Получаем путь к директории проекта
PROJECT_DIR=$(dirname "$(readlink -f "$0")")

echo "Директория проекта: $PROJECT_DIR"
echo "Пользователь сервера: metriks66"
echo ""

# Проверяем, что мы запущены от правильного пользователя
if [ "$USER" != "metriks66" ]; then
    echo "ВНИМАНИЕ: Скрипт запущен от пользователя $USER"
    echo "Рекомендуется запустить от пользователя metriks66"
    echo "Или использовать sudo для изменения владельца файлов"
    echo ""
fi

# Исправляем права доступа к файлам данных
echo "1. Исправление прав доступа к hidden_products.json..."
if [ -f "$PROJECT_DIR/hidden_products.json" ]; then
    chmod 664 "$PROJECT_DIR/hidden_products.json"
    echo "   ✓ Права доступа установлены"
else
    echo "   ⚠ Файл hidden_products.json не найден"
fi

echo "2. Исправление прав доступа к CSV файлу..."
if [ -f "$PROJECT_DIR/store-7407308-202509021623.csv" ]; then
    chmod 664 "$PROJECT_DIR/store-7407308-202509021623.csv"
    echo "   ✓ Права доступа установлены"
else
    echo "   ⚠ CSV файл не найден"
fi

echo "3. Исправление прав доступа к orders.json..."
if [ -f "$PROJECT_DIR/orders.json" ]; then
    chmod 664 "$PROJECT_DIR/orders.json"
    echo "   ✓ Права доступа установлены"
else
    echo "   ⚠ Файл orders.json не найден, создаем его..."
    echo '[]' > "$PROJECT_DIR/orders.json"
    chmod 664 "$PROJECT_DIR/orders.json"
    echo "   ✓ Файл создан с правильными правами"
fi

echo "4. Исправление прав доступа к settings.json..."
if [ -f "$PROJECT_DIR/settings.json" ]; then
    chmod 664 "$PROJECT_DIR/settings.json"
    echo "   ✓ Права доступа установлены"
else
    echo "   ⚠ Файл settings.json не найден, создаем его..."
    echo '{}' > "$PROJECT_DIR/settings.json"
    chmod 664 "$PROJECT_DIR/settings.json"
    echo "   ✓ Файл создан с правильными правами"
fi

# Устанавливаем владельца файлов
echo ""
echo "5. Установка владельца файлов..."
USER_OWNER="metriks66"

echo "   Установка владельца: $USER_OWNER"

# Используем sudo если нужно
if [ "$USER" != "metriks66" ]; then
    echo "   Используем sudo для изменения владельца..."
    sudo chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/hidden_products.json" 2>/dev/null
    sudo chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/store-7407308-202509021623.csv" 2>/dev/null
    sudo chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/orders.json" 2>/dev/null
    sudo chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/settings.json" 2>/dev/null
else
    chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/hidden_products.json" 2>/dev/null
    chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/store-7407308-202509021623.csv" 2>/dev/null
    chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/orders.json" 2>/dev/null
    chown $USER_OWNER:$USER_OWNER "$PROJECT_DIR/settings.json" 2>/dev/null
fi

echo "   ✓ Владелец файлов установлен"

# Проверяем права доступа
echo ""
echo "6. Проверка прав доступа:"
echo "   hidden_products.json:"
ls -la "$PROJECT_DIR/hidden_products.json" 2>/dev/null || echo "     Файл не найден"
echo "   store-7407308-202509021623.csv:"
ls -la "$PROJECT_DIR/store-7407308-202509021623.csv" 2>/dev/null || echo "     Файл не найден"
echo "   orders.json:"
ls -la "$PROJECT_DIR/orders.json" 2>/dev/null || echo "     Файл не найден"
echo "   settings.json:"
ls -la "$PROJECT_DIR/settings.json" 2>/dev/null || echo "     Файл не найден"

echo ""
echo "=========================================="
echo "Готово! Права доступа исправлены."
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo "1. Перезапустите веб-сервер:"
echo "   sudo systemctl restart metriks"
echo "   или"
echo "   sudo systemctl restart gunicorn"
echo ""
echo "2. Проверьте работу админ панели:"
echo "   https://metriks96.ru/admin"
echo ""
echo "3. Если проблемы остаются, проверьте логи:"
echo "   sudo journalctl -u metriks -f"
echo ""
echo "4. Проверьте, что веб-сервер запущен от пользователя metriks66:"
echo "   ps aux | grep gunicorn"
echo ""
