#!/bin/bash
set -e

# Directorio base del proyecto
BASE_DIR=$(dirname "$(dirname "$0")")
API_DIR="$BASE_DIR/apps/api"
ENV_DIR="$BASE_DIR/docker/env"

# Función para mostrar ayuda
show_help() {
  echo "Script para ejecutar migraciones de Alembic con variables de ambiente"
  echo ""
  echo "Uso: $0 [ambiente] [comando] [opciones]"
  echo ""
  echo "Ambientes:"
  echo "  dev, development    Ambiente de desarrollo (default)"
  echo "  test, testing       Ambiente de pruebas"
  echo "  prod, production    Ambiente de producción"
  echo ""
  echo "Comandos y opciones:"
  echo "  upgrade [--rev]     Aplicar migraciones (hasta revisión opcional)"
  echo "  downgrade [--rev]   Revertir migraciones (hasta revisión opcional)"
  echo "  revision [--message] [--autogenerate]  Crear nueva migración"
  echo "  current             Mostrar migración actual"
  echo "  history             Mostrar historial de migraciones"
  echo "  merge               Fusionar múltiples cabezas"
  echo ""
  echo "Ejemplos:"
  echo "  $0 dev upgrade                        # Aplicar todas las migraciones en desarrollo"
  echo "  $0 test revision --message 'nueva tabla' --autogenerate   # Generar migración en pruebas"
  echo "  $0 prod downgrade --rev -1           # Revertir última migración en producción"
}



# Validar argumentos
if [ $# -lt 1 ]; then
  show_help
  exit 1
fi

# Obtener ambiente y comando
ENV=${1}

# Cargar variables de entorno según el ambiente
ENV_FILE=""
case "$ENV" in
  dev)
    ENV_FILE="$ENV_DIR/.env.dev"
    ;;
  test)
    ENV_FILE="$ENV_DIR/.env.test"
    ;;
  prod)
    ENV_FILE="$ENV_DIR/.env.prod"
    ;;
esac

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: No se encontró el archivo de variables de entorno: $ENV_FILE"
  exit 1
fi

# Cargar variables de entorno
echo "Cargando variables de ambiente desde $ENV_FILE"
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Validar existencia de variables requeridas para Alembic
required_vars=("ALEMBIC_DB_HOST" "ALEMBIC_DB_PORT" "ALEMBIC_DB_USER" "ALEMBIC_DB_PASS" "ALEMBIC_DB_NAME" "ALEMBIC_ENVIRONMENT")
missing_vars=()

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo "Error: Faltan variables de entorno requeridas:"
  printf "  - %s\n" "${missing_vars[@]}"
  echo "Por favor, asegúrate de que estas variables estén definidas en $ENV_FILE"
  exit 1
fi

echo "Variables de ambiente validadas correctamente"

# Mostrar las variables de entorno configuradas para la ejecución
echo "Ejecutando con las siguientes configuraciones:"
echo "  - Host: ${ALEMBIC_DB_HOST}"
echo "  - Puerto: ${ALEMBIC_DB_PORT}"
echo "  - Base de datos: ${ALEMBIC_DB_NAME}"
echo "  - Usuario: ${ALEMBIC_DB_USER}"
echo "  - Ambiente: ${ALEMBIC_ENVIRONMENT}"

# # Mapear variables específicas de ambiente a las generales que usa db_config.py
# case "$ENV" in
#   development)
#     export DB_HOST="${DEV_DB_HOST}"
#     export DB_PORT="${DEV_DB_PORT}"
#     export DB_NAME="${DEV_DB_NAME}"
#     export DB_USER="${DEV_DB_USER}"
#     export DB_PASSWORD="${DEV_DB_PASS}"
#     export ENVIRONMENT="development"  
#     ;;
#   testing)
#     export DB_HOST="${TEST_DB_HOST:-localhost}"
#     export DB_PORT="${TEST_DB_PORT:-5432}"
#     export DB_NAME="${TEST_DB_NAME:-moneydiary_test}"
#     export DB_USER="${TEST_DB_USER:-postgres}"
#     export DB_PASSWORD="${TEST_DB_PASS:-postgres}"
#     export ENVIRONMENT="test"  
#     ;;
#   production)
#     export DB_HOST="${PROD_DB_HOST:-localhost}"
#     export DB_PORT="${PROD_DB_PORT:-5432}"
#     export DB_NAME="${PROD_DB_NAME:-moneydiary}"
#     export DB_USER="${PROD_DB_USER:-postgres}"
#     export DB_PASSWORD="${PROD_DB_PASS:-postgres}"
#     export ENVIRONMENT="production"  
#     ;;
# esac


# # Construir argumentos para el script de migración
# MIGRATE_ARGS="--env $ENV $COMMAND"

# # Agregar opciones adicionales
# while [ $# -gt 0 ]; do
#   MIGRATE_ARGS="$MIGRATE_ARGS $1"
#   shift
# done

# # Ejecutar el script de migración Python
# echo "Ejecutando migración con ambiente $ENV: python migrate.py $MIGRATE_ARGS"


# cd "$API_DIR" && python3 migrate.py $MIGRATE_ARGS
