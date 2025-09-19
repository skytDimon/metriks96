# Быстрое исправление проблем с админ панелью

## Проблема
Админ панель не работает - не скрываются и не изменяются товары.

## Причина
Проблема с правами доступа к файлам на сервере.

## Решение

### 1. Запустите скрипт исправления прав доступа на сервере:

```bash
# На сервере выполните:
chmod 664 hidden_products.json
chmod 664 store-7407308-202509021623.csv
chmod 664 orders.json
chmod 664 settings.json

# Установите правильного владельца (замените www-data на пользователя веб-сервера):
chown www-data:www-data hidden_products.json
chown www-data:www-data store-7407308-202509021623.csv
chown www-data:www-data orders.json
chown www-data:www-data settings.json
```

### 2. Или используйте готовый скрипт:

```bash
# Сделайте скрипт исполняемым и запустите:
chmod +x fix_file_permissions.sh
./fix_file_permissions.sh
```

### 3. Перезапустите веб-сервер:

```bash
# Для systemd:
sudo systemctl restart metriks

# Или для gunicorn:
sudo systemctl restart gunicorn

# Или перезапустите вручную
```

## Проверка

После исправления:
1. Зайдите в админ панель
2. Попробуйте скрыть товар
3. Попробуйте отредактировать товар

Если проблемы остаются, проверьте логи веб-сервера:
```bash
sudo journalctl -u metriks -f
```

## Альтернативное решение

Если проблема в том, что веб-сервер запущен не от того пользователя, измените пользователя в systemd сервисе:

```bash
sudo nano /etc/systemd/system/metriks.service
```

Измените строку:
```
User=www-data
Group=www-data
```

На:
```
User=ваш_пользователь
Group=ваш_пользователь
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl restart metriks
```
