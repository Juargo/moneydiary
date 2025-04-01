#!/bin/bash

# Definir el directorio base
BASE_DIR="$(pwd)"

echo "===== Deteniendo contenedores existentes ====="
docker-compose -f docker-compose.prod.yml down

echo "===== Iniciando contenedores ====="
docker-compose -f docker-compose.prod.yml up -d

echo "===== Verificando contenedores ====="
docker ps

echo ""
echo "===== Instalación completada ====="
echo "El frontend está ahora disponible en: http://jorgedev.cl"
echo "La API está disponible en: http://jorgedev.cl:8000"
echo ""
echo "Para ver los logs: docker-compose -f docker-compose.prod.yml logs -f"
