# 🚀 Быстрый старт для продакшна

## ⚡ За 5 минут на сервере

### 1. Подготовка (1 минута)

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Загрузка проекта (1 минута)

```bash
# Клонируйте или загрузите проект
git clone <your-repo> metriks96
cd metriks96

# Или загрузите архив
wget <your-archive> && tar -xzf metriks96.tar.gz && cd metriks96
```

### 3. Настройка (2 минуты)

```bash
# Скопируйте конфигурацию
cp env.example .env

# ОТРЕДАКТИРУЙТЕ .env файл!
nano .env
```

**Обязательно заполните в `.env`:**
```bash
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
TELEGRAM_CHAT_IDS=ваш_chat_id
SMTP_PASSWORD=пароль_от_email
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 4. Запуск (1 минута)

```bash
# Запустите автоматический деплой
chmod +x deploy.sh
./deploy.sh

# Выберите вариант 1 (Docker Compose)
```

### 5. Проверка

```bash
# Проверьте статус
docker-compose ps

# Проверьте логи
docker-compose logs -f

# Откройте сайт
curl http://localhost
```

## 🎯 Готово!

Ваш сайт доступен по адресу: `http://your-server-ip`

## 🔧 Настройка домена (опционально)

```bash
# Установите Nginx
sudo apt install nginx

# Настройте домен
sudo nano /etc/nginx/sites-available/metriks

# Получите SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 📞 Поддержка

- 📖 Полная документация: `README.md`
- 🔒 Безопасность: `SECURITY.md`
- 🚀 Деплой: `DEPLOYMENT.md`
- ✅ Чек-лист: `PRODUCTION_CHECKLIST.md`

## 🆘 Быстрая помощь

```bash
# Проверка статуса
docker-compose ps

# Перезапуск
docker-compose restart

# Логи
docker-compose logs -f metriks

# Тест Telegram
curl http://localhost:8000/api/test-telegram

# Health check
curl http://localhost:8000/health
```
