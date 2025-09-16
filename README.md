# МЕТРИКС - Современный интернет-магазин крепежных изделий

Современное веб-приложение для компании МЕТРИКС, специализирующейся на поставке крепежных изделий в Екатеринбурге.

## 🚀 Особенности

- **Современный дизайн**: Адаптивный интерфейс с Bootstrap 5
- **FastAPI Backend**: Высокопроизводительный API на Python
- **Работа с CSV**: Загрузка товаров из CSV файла без базы данных
- **Корзина покупок**: Локальное хранение с синхронизацией
- **Каталог товаров**: Поиск и фильтрация по категориям
- **Детальные страницы**: Просмотр размеров и характеристик товаров
- **Мобильная версия**: Полная поддержка мобильных устройств
- **Telegram интеграция**: Автоматическая отправка заявок в Telegram бот
- **Production Ready**: Готов к деплою на продакшн с Docker и systemd
- **Безопасность**: Переменные окружения, .gitignore, защита от уязвимостей

## 📋 Требования

### Для разработки:
- Python 3.8+
- CSV файл с товарами
- Современный веб-браузер

### Для продакшна:
- Python 3.8+ или Docker
- Nginx (опционально, для reverse proxy)
- SSL сертификат (рекомендуется)
- Telegram Bot Token
- SMTP настройки для email

## 🛠 Установка и запуск

### 🚀 Быстрый деплой на продакшн

```bash
# 1. Клонируйте проект
git clone <repository-url>
cd metriks96

# 2. Настройте переменные окружения
cp env.example .env
nano .env  # Заполните реальными значениями

# 3. Запустите автоматический деплой
chmod +x deploy.sh
./deploy.sh
```

### 🔧 Ручная установка для разработки

#### 1. Клонирование и установка зависимостей

```bash
# Создание виртуального окружения
python3 -m venv env

# Активация окружения
# На Windows:
env\Scripts\activate
# На macOS/Linux:
source env/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

#### 2. Подготовка данных

Убедитесь, что в корневой папке проекта есть CSV файл с товарами:
- `store-7407308-202509021623.csv` - основной файл с товарами

#### 3. Настройка переменных окружения

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Отредактируйте файл .env
nano .env
```

**Обязательные переменные:**
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
- `TELEGRAM_CHAT_IDS` - ID чатов для уведомлений (через запятую)
- `SMTP_PASSWORD` - пароль от email для отправки заявок

#### 4. Запуск приложения

```bash
# Простой запуск для разработки
python run.py

# Или альтернативно:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

## 🚀 Деплой на продакшн

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Настройте переменные окружения
cp env.example .env
nano .env

# Запустите через Docker Compose
docker-compose up -d

# Проверьте статус
docker-compose ps
docker-compose logs -f
```

### Вариант 2: Systemd Service

```bash
# Настройте переменные окружения
cp env.example .env
nano .env

# Установите systemd service
sudo cp metriks.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable metriks
sudo systemctl start metriks

# Проверьте статус
sudo systemctl status metriks
sudo journalctl -u metriks -f
```

### Вариант 3: Nginx + Gunicorn

```bash
# Установите Nginx
sudo apt update
sudo apt install nginx

# Скопируйте конфигурацию Nginx
sudo cp nginx.conf /etc/nginx/sites-available/metriks
sudo ln -s /etc/nginx/sites-available/metriks /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Запустите приложение через Gunicorn
gunicorn -c gunicorn.conf.py app.main:app
```

### 🔒 Настройка SSL (рекомендуется)

```bash
# Установите Certbot
sudo apt install certbot python3-certbot-nginx

# Получите SSL сертификат
sudo certbot --nginx -d yourdomain.com

# Автоматическое обновление
sudo crontab -e
# Добавьте: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Структура CSV файла

Приложение автоматически загружает товары из CSV файла со следующими полями:

**Основные поля:**
- `Tilda UID` - уникальный ID товара
- `Title` - название товара
- `Description` / `Text` - описание
- `Category` - категория
- `Photo` - ссылка на изображение
- `Brand` - бренд
- `SKU` - артикул

**Характеристики:**
- `Characteristics:Материал` - материал
- `Characteristics:Применение` - применение
- `Characteristics:Аналоги` - аналоги
- `Characteristics:d / l` - диаметр/длина
- `Weight`, `Length`, `Width`, `Height` - размеры

## 📁 Структура проекта

```
metriks96/
├── app/                    # Основное приложение
│   ├── routers/           # API маршруты
│   │   └── products.py    # Детали товаров
│   ├── main.py            # Главный файл приложения
│   └── __init__.py
├── templates/              # HTML шаблоны
│   ├── base.html          # Базовый шаблон
│   ├── catalog.html       # Каталог товаров
│   ├── product_detail.html # Детали товара
│   ├── cart.html          # Корзина
│   └── 404.html           # Страница 404
├── static/                 # Статические файлы
│   ├── css/               # Стили
│   ├── js/                # JavaScript
│   └── images/            # Изображения
├── store-7407308-202509021623.csv # Файл с товарами
├── run.py                 # Скрипт запуска
└── requirements.txt       # Зависимости Python
```

## 🔧 Функциональность

### Каталог товаров
- Просмотр всех товаров
- Фильтрация по категориям
- Поиск по названию и описанию
- Сортировка

### Детальные страницы товаров
- Полная информация о товаре
- Размеры и характеристики
- Кнопка "Добавить в корзину"
- Похожие товары

### Корзина покупок
- Добавление товаров
- Указание количества
- Комментарии к товарам
- Оформление заявки

## 🚀 Быстрый старт

1. **Клонируйте проект**
2. **Создайте виртуальное окружение**: `python -m venv env`
3. **Активируйте окружение**: `source env/bin/activate` (macOS/Linux) или `env\Scripts\activate` (Windows)
4. **Установите зависимости**: `pip install -r requirements.txt`
5. **Запустите приложение**: `python run.py`
6. **Откройте браузер**: http://localhost:8000

## 📊 Мониторинг и обслуживание

### Проверка статуса

```bash
# Docker Compose
docker-compose ps
docker-compose logs -f metriks

# Systemd
sudo systemctl status metriks
sudo journalctl -u metriks -f

# Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/access.log
```

### Обновление товаров

```bash
# Замените CSV файл
cp new_products.csv store-7407308-202509021623.csv

# Перезапустите приложение
# Docker:
docker-compose restart metriks

# Systemd:
sudo systemctl restart metriks

# Gunicorn:
pkill -f gunicorn
gunicorn -c gunicorn.conf.py app.main:app &
```

### Резервное копирование

```bash
# Создайте резервную копию
tar -czf metriks-backup-$(date +%Y%m%d).tar.gz \
  --exclude='env' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  .

# Восстановление
tar -xzf metriks-backup-YYYYMMDD.tar.gz
```

### Логи и отладка

```bash
# Просмотр логов приложения
tail -f logs/app.log

# Просмотр логов Nginx
tail -f /var/log/nginx/error.log

# Тест Telegram бота
curl http://localhost:8000/api/test-telegram

# Проверка здоровья
curl http://localhost:8000/health
```

## 🔧 Настройка Telegram бота

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота
3. Узнайте ваш chat_id:
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
   ```
4. Добавьте токен и chat_id в файл `.env`

## 📝 Примечания

- Приложение работает полностью без базы данных
- Все данные загружаются из CSV файла при запуске
- Корзина хранится в localStorage браузера
- Для изменения товаров редактируйте CSV файл
- Все секретные данные хранятся в переменных окружения
- Приложение оптимизировано для слабых серверов (1GB RAM)
