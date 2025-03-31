#!/bin/bash

# Definir el directorio base
BASE_DIR="/Users/juargo/Documents/GitHub/moneydiary/docker"

# Crear directorio para certificados
mkdir -p ${BASE_DIR}/nginx/certs

# Crear certificado SSL autofirmado temporal
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ${BASE_DIR}/nginx/certs/dummy.key \
  -out ${BASE_DIR}/nginx/certs/dummy.crt \
  -subj '/CN=localhost' \
  -addext "subjectAltName = DNS:jorgedev.cl,DNS:www.jorgedev.cl"

# Crear directorios necesarios
mkdir -p ${BASE_DIR}/nginx/www
mkdir -p ${BASE_DIR}/nginx/www/.well-known
mkdir -p ${BASE_DIR}/nginx/www/.well-known/acme-challenge

# Establecer permisos correctos
chmod -R 755 ${BASE_DIR}/nginx/www
chmod -R 755 ${BASE_DIR}/nginx/certs

echo "Certificados temporales y directorios creados correctamente."
echo "Por favor, ejecute los siguientes comandos:"
echo "docker-compose -f ${BASE_DIR}/docker-compose.prod.yml down"
echo "docker-compose -f ${BASE_DIR}/docker-compose.prod.yml up -d"
echo "Una vez que los contenedores estén funcionando, ejecute:"
echo "docker-compose -f ${BASE_DIR}/docker-compose.prod.yml run --rm certbot"
