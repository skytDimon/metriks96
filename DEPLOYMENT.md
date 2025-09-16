# 🚀 Руководство по деплою

## 📋 Подготовка к деплою

### 1. Подготовка сервера

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите необходимые пакеты
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Установите Docker (опционально)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Клонирование проекта

```bash
# Клонируйте репозиторий
git clone <your-repository-url>
cd metriks96

# Или загрузите архив
wget <your-archive-url>
tar -xzf metriks96.tar.gz
cd metriks96
```

### 3. Настройка переменных окружения

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Отредактируйте файл .env
nano .env
```

**Обязательно заполните:**
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
- `TELEGRAM_CHAT_IDS` - ID чатов для уведомлений
- `SMTP_PASSWORD` - пароль от email
- `SECRET_KEY` - случайная строка для безопасности

## 🐳 Деплой через Docker (рекомендуется)

### Быстрый запуск

```bash
# Запустите автоматический деплой
chmod +x deploy.sh
./deploy.sh
```

### Ручной запуск

```bash
# Соберите и запустите контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps
docker-compose logs -f
```

### Обновление

```bash
# Остановите контейнеры
docker-compose down

# Обновите код
git pull

# Пересоберите и запустите
docker-compose up -d --build
```

## ⚙️ Деплой через Systemd

### 1. Подготовка окружения

```bash
# Создайте виртуальное окружение
python3 -m venv env
source env/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка systemd service

```bash
# Скопируйте service файл
sudo cp metriks.service /etc/systemd/system/

# Отредактируйте пути в service файле
sudo nano /etc/systemd/system/metriks.service

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable metriks

# Запустите сервис
sudo systemctl start metriks
```

### 3. Проверка статуса

```bash
# Проверьте статус
sudo systemctl status metriks

# Просмотрите логи
sudo journalctl -u metriks -f
```

## 🌐 Настройка Nginx

### 1. Установка Nginx

```bash
# Установите Nginx
sudo apt install nginx

# Запустите Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. Конфигурация

```bash
# Скопируйте конфигурацию
sudo cp nginx.conf /etc/nginx/sites-available/metriks

# Создайте символическую ссылку
sudo ln -s /etc/nginx/sites-available/metriks /etc/nginx/sites-enabled/

# Удалите дефолтную конфигурацию
sudo rm /etc/nginx/sites-enabled/default

# Проверьте конфигурацию
sudo nginx -t

# Перезагрузите Nginx
sudo systemctl reload nginx
```

### 3. Настройка SSL

```bash
# Установите Certbot
sudo apt install certbot python3-certbot-nginx

# Получите SSL сертификат
sudo certbot --nginx -d yourdomain.com

# Проверьте автообновление
sudo certbot renew --dry-run
```

## 📊 Мониторинг

### Проверка статуса

```bash
# Docker
docker-compose ps
docker-compose logs -f metriks

# Systemd
sudo systemctl status metriks
sudo journalctl -u metriks -f

# Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/access.log
```

### Health Check

```bash
# Проверьте доступность
curl http://localhost:8000/
curl http://localhost/health

# Тест Telegram
curl http://localhost:8000/api/test-telegram
```

## 🔄 Обновление приложения

### Обновление товаров

```bash
# Замените CSV файл
cp new_products.csv store-7407308-202509021623.csv

# Перезапустите приложение
# Docker:
docker-compose restart metriks

# Systemd:
sudo systemctl restart metriks
```

### Обновление кода

```bash
# Остановите приложение
# Docker:
docker-compose down

# Systemd:
sudo systemctl stop metriks

# Обновите код
git pull

# Запустите заново
# Docker:
docker-compose up -d

# Systemd:
sudo systemctl start metriks
```

## 🛠️ Устранение неполадок

### Проблемы с запуском

```bash
# Проверьте логи
docker-compose logs metriks
sudo journalctl -u metriks -f

# Проверьте переменные окружения
cat .env

# Проверьте права доступа
ls -la .env
chmod 600 .env
```

### Проблемы с Telegram

```bash
# Проверьте токен
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"

# Проверьте chat_id
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

### Проблемы с Nginx

```bash
# Проверьте конфигурацию
sudo nginx -t

# Проверьте логи
sudo tail -f /var/log/nginx/error.log

# Перезапустите Nginx
sudo systemctl restart nginx
```

## 📝 Полезные команды

```bash
# Создание резервной копии
tar -czf backup-$(date +%Y%m%d).tar.gz --exclude='env' --exclude='.git' .

# Очистка Docker
docker system prune -a

# Просмотр использования ресурсов
docker stats
htop

# Проверка портов
netstat -tlnp | grep :8000
```

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Убедитесь, что все переменные окружения настроены
3. Проверьте доступность портов
4. Убедитесь, что файлы имеют правильные права доступа
5. Проверьте статус всех сервисов
