#!/bin/bash

# Crear directorio para certificados
mkdir -p /Users/juargo/Documents/GitHub/moneydiary/docker/nginx/certs

# Crear certificado SSL autofirmado temporal
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /Users/juargo/Documents/GitHub/moneydiary/docker/nginx/certs/dummy.key \
  -out /Users/juargo/Documents/GitHub/moneydiary/docker/nginx/certs/dummy.crt \
  -subj '/CN=localhost'

# Crear directorios necesarios
mkdir -p /Users/juargo/Documents/GitHub/moneydiary/docker/nginx/www
mkdir -p /Users/juargo/Documents/GitHub/moneydiary/docker/nginx/acme-challenge

echo "Certificados temporales y directorios creados correctamente."
