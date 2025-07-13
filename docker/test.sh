#!/bin/bash
# Script para iniciar entorno de testing con Docker Compose

# Determinar la ruta base del proyecto
BASE_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
cd $BASE_DIR

# Cargar variables de entorno para testing
cp docker/env/.env.test .env
export $(grep -v '^#' .env | xargs)

# Iniciar servicios
docker compose -f docker/compose/docker-compose.base.yml -f docker/compose/docker-compose.test.yml up -d

# Comprobar si los servicios están levantados
echo "Esperando a que los servicios estén disponibles..."
sleep 5

# Verificar servicios
echo "Verificando servicios:"
docker compose ps

echo "Entorno de TESTING iniciado correctamente. Puedes acceder a:"
echo "- API: http://localhost:${API_PORT:-8001}"
echo "- Frontend: http://localhost:${WEB_PORT:-3001}"
echo "- Test Runner: Ejecuta 'docker compose -f docker/compose/docker-compose.base.yml -f docker/compose/docker-compose.test.yml run test-runner'"
