#!/bin/bash
echo "🔄 Обновляем SSL сертификаты..."
docker-compose run --rm certbot renew
docker-compose restart nginx
echo "✅ SSL сертификаты обновлены!"
