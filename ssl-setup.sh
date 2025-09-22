#!/bin/bash

# Скрипт для настройки SSL сертификатов Let's Encrypt
# Замените your-domain.com и your-email@example.com на ваши данные

DOMAIN="metriks96.ru"
EMAIL="metriks66@bk.ru"

echo "🔐 Настройка SSL сертификатов для домена: $DOMAIN"
echo "📧 Email: $EMAIL"

# Проверяем, что домен указан
if [ "$DOMAIN" = "metriks961.ru" ]; then
    echo "❌ Ошибка: Замените your-domain.com на ваш реальный домен в файле ssl-setup.sh"
    exit 1
fi

if [ "$EMAIL" = "metriks66@b1k.ru" ]; then
    echo "❌ Ошибка: Замените your-email@example.com на ваш реальный email в файле ssl-setup.sh"
    exit 1
fi

# Обновляем nginx.conf с правильным доменом
echo "📝 Обновляем nginx.conf с доменом $DOMAIN"
sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf

# Обновляем docker-compose.yml с правильным email и доменом
echo "📝 Обновляем docker-compose.yml с email $EMAIL и доменом $DOMAIN"
sed -i "s/your-email@example.com/$EMAIL/g" docker-compose.yml
sed -i "s/your-domain.com/$DOMAIN/g" docker-compose.yml

# Создаем временную конфигурацию nginx для получения сертификата
echo "🔧 Создаем временную конфигурацию nginx..."
cat > nginx-temp.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    upstream metriks_backend {
        server metriks:8000;
    }

    server {
        listen 80;
        server_name $DOMAIN;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            proxy_pass http://metriks_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF

# Запускаем контейнеры с временной конфигурацией
echo "🚀 Запускаем контейнеры с временной конфигурацией..."
cp nginx.conf nginx-original.conf
cp nginx-temp.conf nginx.conf

docker compose up -d

# Ждем запуска nginx
echo "⏳ Ждем запуска nginx..."
sleep 10

# Получаем SSL сертификат
echo "🔐 Получаем SSL сертификат..."
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN

# Восстанавливаем полную конфигурацию nginx
echo "🔄 Восстанавливаем полную конфигурацию nginx..."
cp nginx-original.conf nginx.conf

# Перезапускаем nginx с SSL
echo "🔄 Перезапускаем nginx с SSL..."
docker-compose restart nginx

# Создаем скрипт для автоматического обновления сертификатов
echo "📝 Создаем скрипт для автоматического обновления сертификатов..."
cat > renew-ssl.sh << 'EOF'
#!/bin/bash
echo "🔄 Обновляем SSL сертификаты..."
docker-compose run --rm certbot renew
docker-compose restart nginx
echo "✅ SSL сертификаты обновлены!"
EOF

chmod +x renew-ssl.sh

# Добавляем задачу в crontab для автоматического обновления
echo "⏰ Добавляем задачу в crontab для автоматического обновления сертификатов..."
(crontab -l 2>/dev/null; echo "0 12 * * * $(pwd)/renew-ssl.sh >> $(pwd)/ssl-renewal.log 2>&1") | crontab -

echo "✅ Настройка SSL завершена!"
echo "🌐 Ваш сайт теперь доступен по HTTPS: https://$DOMAIN"
echo "🔄 Сертификаты будут автоматически обновляться каждый день в 12:00"
echo "📝 Логи обновления сохраняются в файл ssl-renewal.log"
