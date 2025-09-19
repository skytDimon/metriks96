# Устранение неполадок

## Проблема: Не работает скрытие товаров на сервере

### Симптомы
- На localhost скрытие товаров работает корректно
- На сервере при попытке скрыть товар появляется ошибка
- В админ-панели показывается сообщение об ошибке

### Возможные причины

1. **Права доступа к файлу `hidden_products.json`**
   - Приложение не может записать в файл из-за недостаточных прав
   - Файл принадлежит другому пользователю

2. **Отсутствие файла `hidden_products.json`**
   - Файл не был создан при деплое
   - Файл был удален или перемещен

3. **Проблемы с Docker volumes**
   - Неправильная настройка volume в docker-compose.yml
   - Конфликт прав между контейнером и хостом

### Решение

#### Шаг 1: Проверка логов
```bash
# Для Docker Compose
docker-compose logs -f metriks

# Для systemd
sudo journalctl -u metriks -f
```

#### Шаг 2: Проверка прав доступа
```bash
# Проверяем права на файлы
ls -la hidden_products.json orders.json

# Проверяем, под каким пользователем запускается приложение
docker-compose exec metriks whoami
```

#### Шаг 3: Исправление прав доступа
```bash
# Запускаем скрипт исправления прав
sudo ./fix_permissions.sh
```

#### Шаг 4: Ручное исправление (если скрипт не помог)
```bash
# Создаем файл если его нет
echo '{"hidden_products": []}' > hidden_products.json

# Устанавливаем права (замените USER:GROUP на нужные)
sudo chown USER:GROUP hidden_products.json
sudo chmod 664 hidden_products.json

# Для Docker - проверяем пользователя в контейнере
docker-compose exec metriks id
```

#### Шаг 5: Проверка Docker volumes
Убедитесь, что в `docker-compose.yml` правильно настроен volume:
```yaml
volumes:
  - ./hidden_products.json:/app/hidden_products.json
```

#### Шаг 6: Перезапуск приложения
```bash
# Для Docker Compose
docker-compose restart metriks

# Для systemd
sudo systemctl restart metriks
```

### Дополнительная диагностика

#### Проверка работы функций скрытия товаров
```bash
# Подключаемся к контейнеру
docker-compose exec metriks python

# Тестируем функции
from app.main import load_hidden_products, save_hidden_products, hide_product
print("Загружаем скрытые товары:", load_hidden_products())
print("Тестируем скрытие товара:", hide_product("test_id"))
print("Проверяем результат:", load_hidden_products())
```

#### Проверка файловой системы
```bash
# Проверяем доступность записи
docker-compose exec metriks touch /app/test_write.txt
docker-compose exec metriks rm /app/test_write.txt
```

### Профилактика

1. **Всегда используйте скрипт деплоя** `deploy.sh`
2. **Проверяйте права доступа** после деплоя
3. **Мониторьте логи** приложения
4. **Используйте Docker volumes** для персистентных данных

### Контакты
Если проблема не решается, проверьте:
- Логи приложения
- Права доступа к файлам
- Настройки Docker volumes
- Конфигурацию systemd (если используется)
