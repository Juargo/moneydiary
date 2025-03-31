#!/bin/bash

# Definir el directorio base
BASE_DIR="/Users/juargo/Documents/GitHub/moneydiary/docker"

# Ejecutar el script para configurar certificados
bash ${BASE_DIR}/nginx/setup-certs.sh

# Detener contenedores existentes
docker-compose -f ${BASE_DIR}/docker-compose.prod.yml down

# Iniciar contenedores
docker-compose -f ${BASE_DIR}/docker-compose.prod.yml up -d

echo "Contenedores iniciados. Esperando 15 segundos antes de solicitar certificados SSL..."
sleep 15

# Ejecutar certbot para obtener certificados reales
docker-compose -f ${BASE_DIR}/docker-compose.prod.yml run --rm certbot

echo ""
echo "Si Certbot se completó correctamente, actualice la configuración de Nginx en:"
echo "${BASE_DIR}/nginx/conf.d/default.conf"
echo ""
echo "Cambie las líneas:"
echo "ssl_certificate /etc/nginx/certs/dummy.crt;"
echo "ssl_certificate_key /etc/nginx/certs/dummy.key;"
echo ""
echo "Por:"
echo "ssl_certificate /etc/letsencrypt/live/jorgedev.cl/fullchain.pem;"
echo "ssl_certificate_key /etc/letsencrypt/live/jorgedev.cl/privkey.pem;"
echo ""
echo "Luego reinicie Nginx con:"
echo "docker-compose -f ${BASE_DIR}/docker-compose.prod.yml restart nginx"
