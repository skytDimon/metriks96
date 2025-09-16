# 🔒 Руководство по безопасности

## ⚠️ Критически важно перед деплоем!

### 1. Настройка переменных окружения

**НИКОГДА не коммитьте файл `.env` в Git!**

```bash
# Создайте файл .env из примера
cp env.example .env

# Отредактируйте файл .env
nano .env
```

### 2. Обязательные переменные

```bash
# Telegram Bot (ОБЯЗАТЕЛЬНО)
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_IDS=your_chat_id1,your_chat_id2

# Email (ОБЯЗАТЕЛЬНО)
SMTP_PASSWORD=your_actual_email_password

# Безопасность (ОБЯЗАТЕЛЬНО)
SECRET_KEY=your_very_long_random_secret_key_here
DEBUG=False
```

### 3. Получение Telegram Bot Token

1. Напишите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env`

### 4. Получение Chat ID

```bash
# Отправьте сообщение боту, затем выполните:
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"

# Найдите "chat":{"id":123456789} в ответе
```

### 5. Проверка безопасности

```bash
# Убедитесь, что .env не в Git
git status

# Проверьте права доступа к .env
chmod 600 .env

# Проверьте, что секреты не в коде
grep -r "8404842448" . --exclude-dir=.git
grep -r "your_password_here" . --exclude-dir=.git
```

## 🛡️ Дополнительные меры безопасности

### Firewall

```bash
# Настройте UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8000  # Закройте прямой доступ к приложению
```

### SSL/HTTPS

```bash
# Установите SSL сертификат
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Обновления

```bash
# Регулярно обновляйте систему
sudo apt update && sudo apt upgrade

# Обновляйте зависимости Python
pip install --upgrade -r requirements.txt
```

### Мониторинг

```bash
# Настройте логирование
sudo mkdir -p /var/log/metriks
sudo chown www-data:www-data /var/log/metriks

# Мониторинг логов
tail -f /var/log/metriks/error.log
```

## 🚨 Что НЕ делать

- ❌ Не коммитьте `.env` файл
- ❌ Не оставляйте пароли в коде
- ❌ Не используйте простые пароли
- ❌ Не открывайте порт 8000 в firewall
- ❌ Не запускайте приложение от root
- ❌ Не игнорируйте SSL сертификаты

## ✅ Чек-лист безопасности

- [ ] Файл `.env` создан и заполнен
- [ ] Файл `.env` добавлен в `.gitignore`
- [ ] Telegram токен настроен
- [ ] Email пароль настроен
- [ ] SECRET_KEY сгенерирован
- [ ] DEBUG=False
- [ ] Firewall настроен
- [ ] SSL сертификат установлен
- [ ] Приложение запущено не от root
- [ ] Логирование настроено

## 🔧 Генерация SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

Или через командную строку:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```
