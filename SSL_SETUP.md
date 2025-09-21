# Настройка SSL сертификатов Let's Encrypt

## Быстрая настройка

1. **Отредактируйте файл `ssl-setup.sh`:**
   ```bash
   nano ssl-setup.sh
   ```
   
   Замените:
   - `your-domain.com` на ваш реальный домен
   - `your-email@example.com` на ваш email

2. **Запустите скрипт настройки:**
   ```bash
   ./ssl-setup.sh
   ```

3. **Проверьте работу HTTPS:**
   ```bash
   curl -I https://your-domain.com
   ```

## Ручная настройка

### 1. Подготовка

Убедитесь, что:
- Домен указывает на ваш сервер
- Порты 80 и 443 открыты
- Docker и Docker Compose установлены

### 2. Получение сертификата

```bash
# Запустите контейнеры
docker-compose up -d

# Получите сертификат
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com
```

### 3. Обновление nginx.conf

Замените `your-domain.com` на ваш домен в файле `nginx.conf`:
```bash
sed -i 's/your-domain.com/your-actual-domain.com/g' nginx.conf
```

### 4. Перезапуск nginx

```bash
docker-compose restart nginx
```

## Автоматическое обновление

Сертификаты Let's Encrypt действительны 90 дней. Для автоматического обновления:

```bash
# Запустите скрипт обновления
./renew-ssl.sh

# Или добавьте в crontab (уже сделано скриптом ssl-setup.sh)
crontab -e
# Добавьте строку:
# 0 12 * * * /path/to/your/project/renew-ssl.sh >> /path/to/your/project/ssl-renewal.log 2>&1
```

## Проверка SSL

```bash
# Проверка сертификата
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Проверка с помощью curl
curl -I https://your-domain.com

# Проверка с помощью SSL Labs
# Откройте https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com
```

## Структура файлов

```
metriks96/
├── nginx.conf              # Конфигурация nginx с SSL
├── docker-compose.yml      # Docker Compose с certbot
├── ssl-setup.sh           # Скрипт автоматической настройки
├── renew-ssl.sh           # Скрипт обновления сертификатов
└── SSL_SETUP.md           # Эта инструкция
```

## Безопасность

Конфигурация включает:
- ✅ TLS 1.2 и 1.3
- ✅ Современные шифры
- ✅ HSTS заголовки
- ✅ Защита от clickjacking
- ✅ Защита от MIME sniffing
- ✅ XSS защита

## Устранение проблем

### Ошибка "Domain not found"
- Убедитесь, что DNS записи настроены правильно
- Проверьте, что домен указывает на ваш сервер

### Ошибка "Rate limit exceeded"
- Let's Encrypt имеет лимиты на количество сертификатов
- Подождите или используйте staging окружение

### Ошибка "Connection refused"
- Проверьте, что порты 80 и 443 открыты
- Убедитесь, что nginx запущен

### Проверка логов
```bash
# Логи nginx
docker-compose logs nginx

# Логи certbot
docker-compose logs certbot

# Логи обновления сертификатов
tail -f ssl-renewal.log
```

## Staging окружение

Для тестирования используйте staging сервер Let's Encrypt:

```bash
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  --staging \
  -d your-domain.com
```

## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Убедитесь, что домен настроен правильно
3. Проверьте, что порты открыты
4. Обратитесь к документации Let's Encrypt: https://letsencrypt.org/docs/
