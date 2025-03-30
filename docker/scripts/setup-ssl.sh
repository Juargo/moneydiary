#!/bin/bash

# Script para configurar certificados SSL para MoneyDiary
# Debe ejecutarse en el servidor de producción

set -e

DOMAIN=$1
EMAIL=$2
MODE=$3

if [ -z "$DOMAIN" ]; then
  echo "Error: Dominio no especificado"
  echo "Uso: $0 dominio.com email@ejemplo.com [production|dev]"
  exit 1
fi

if [ -z "$EMAIL" ]; then
  echo "Error: Email no especificado"
  echo "Uso: $0 dominio.com email@ejemplo.com [production|dev]"
  exit 1
fi

if [ -z "$MODE" ]; then
  MODE="production"
fi

# Crear directorios necesarios
mkdir -p ~/docker/nginx/certs
chmod 755 ~/docker/nginx/certs

if [ "$MODE" == "production" ]; then
  echo "Configurando certificados Let's Encrypt para $DOMAIN..."
  
  # Instalar Certbot si no está instalado
  if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    apt-get update
    apt-get install -y certbot
  fi
  
  # Detener Nginx si está corriendo
  docker-compose -f ~/docker-compose.prod.yml stop nginx 2>/dev/null || true
  
  # Obtener certificado
  certbot certonly --standalone --agree-tos --email $EMAIL -d $DOMAIN -d www.$DOMAIN
  
  # Copiar certificados
  cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ~/docker/nginx/certs/cert.pem
  cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ~/docker/nginx/certs/key.pem
  
  # Configurar renovación automática
  CRON_JOB="0 0,12 * * * root docker-compose -f ~/docker-compose.prod.yml stop nginx && certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ~/docker/nginx/certs/cert.pem && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ~/docker/nginx/certs/key.pem && docker-compose -f ~/docker-compose.prod.yml up -d nginx"
  
  # Verificar si el trabajo cron ya existe
  if ! grep -q "certbot renew" /etc/crontab; then
    echo "$CRON_JOB" | tee -a /etc/crontab > /dev/null
    echo "Renovación automática configurada"
  fi
  
  echo "Certificados Let's Encrypt configurados exitosamente"
  
else
  echo "Generando certificados autofirmados para $DOMAIN..."
  
  # Generar certificados autofirmados
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ~/docker/nginx/certs/key.pem \
    -out ~/docker/nginx/certs/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
  
  echo "Certificados autofirmados generados exitosamente"
fi

# Establecer permisos
chmod 644 ~/docker/nginx/certs/cert.pem ~/docker/nginx/certs/key.pem

# Actualizar configuración de Nginx
sed -i "s/yourdomain.com/$DOMAIN/g" ~/docker/nginx/conf.d/app.conf

# Reiniciar servicios
docker-compose -f ~/docker-compose.prod.yml up -d

echo "Configuración SSL completada. Verifica que tu sitio esté funcionando en https://$DOMAIN"
echo "Si usas certificados autofirmados, tendrás que aceptar la advertencia de seguridad en tu navegador"
