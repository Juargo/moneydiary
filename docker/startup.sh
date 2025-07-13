#!/bin/bash
# Script para iniciar entorno de desarrollo con Docker Compose

# Determinar la ruta base del proyecto
BASE_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
cd $BASE_DIR

# Verificar si .env existe, si no, crear desde .env.example
if [ ! -f .env ]; then
  echo "Archivo .env no encontrado, creando desde docker/env/.env.dev"
  cp docker/env/.env.dev .env
fi

# Cargar variables de entorno
export $(grep -v '^#' .env | xargs)

# Iniciar servicios
docker compose -f docker/compose/docker-compose.base.yml -f docker/compose/docker-compose.dev.yml up -d

# Comprobar si los servicios están levantados
echo "Esperando a que los servicios estén disponibles..."
sleep 5

# Verificar servicios
echo "Verificando servicios:"
docker compose ps

echo "Entorno de DESARROLLO iniciado correctamente. Puedes acceder a:"
echo "- API: http://localhost:${API_PORT:-8000}"
echo "- Frontend: http://localhost:${WEB_PORT:-3000}"
echo "- pgAdmin: http://localhost:5050 (Email: ${PGADMIN_EMAIL:-admin@moneydiary.com}, Password: ${PGADMIN_PASSWORD:-admin_password})"
