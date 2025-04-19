#!/bin/bash
# Script para gestionar el entorno de producción con Docker Compose

# Determinar la ruta base del proyecto
BASE_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
cd $BASE_DIR

# Verificar que estamos en una rama segura (main o producción)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "production" ]]; then
  echo "⚠️ ADVERTENCIA: No estás en la rama main o production ($CURRENT_BRANCH)."
  echo "Esto podría no ser lo que deseas para un despliegue en producción."
  read -p "¿Deseas continuar de todos modos? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operación cancelada."
    exit 1
  fi
fi

# Cargar variables de entorno para producción
cp docker/env/.env.prod .env
export $(grep -v '^#' .env | xargs)

# Ejecutar comando específico o desplegar por defecto
if [ $# -eq 0 ]; then
  echo "Desplegando entorno de PRODUCCIÓN..."
  docker compose -f docker/compose/docker-compose.base.yml -f docker/compose/docker-compose.prod.yml up -d
else
  docker compose -f docker/compose/docker-compose.base.yml -f docker/compose/docker-compose.prod.yml "$@"
fi
