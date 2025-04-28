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

# Normalizar ambiente
normalize_env() {
  case "$1" in
    dev|development)
      echo "development"
      ;;
    test|testing)
      echo "testing"
      ;;
    prod|production)
      echo "production"
      ;;
    *)
      echo "$1"
      ;;
  esac
}



# Función para crear la base de datos si no existe
create_database_if_not_exists() {
  local host="$1"
  local port="$2"
  local dbname="$3"
  local user="$4"
  local password="$5"
  
  echo "Verificando si la base de datos $dbname existe..."
  
  # Comprobar si la base de datos existe
  if PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -lqt | cut -d \| -f 1 | grep -qw "$dbname"; then
    echo "La base de datos $dbname ya existe."
  else
    echo "La base de datos $dbname no existe. Creándola..."
    PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -c "CREATE DATABASE $dbname;"
    echo "Base de datos $dbname creada exitosamente."
  fi

  # Crear el schema app si no existe
  echo "Verificando y creando el esquema 'app' si no existe..."
  PGPASSWORD="$password" psql -h "$host" -p "$port" -U "$user" -d "$dbname" -c "CREATE SCHEMA IF NOT EXISTS app;"
  echo "Esquema 'app' verificado/creado exitosamente."
}


# Validar argumentos
if [ $# -lt 1 ]; then
  show_help
  exit 1
fi

# Obtener ambiente y comando
ENV=$(normalize_env "${1}")
shift
COMMAND="${1}"
shift

# Validar ambiente
case "$ENV" in
  development|testing|production)
    true
    ;;
  *)
    echo "Error: Ambiente no válido: $ENV"
    show_help
    exit 1
    ;;
esac

# Cargar variables de entorno según el ambiente
ENV_FILE=""
case "$ENV" in
  development)
    ENV_FILE="$ENV_DIR/.env.dev"
    ;;
  testing)
    ENV_FILE="$ENV_DIR/.env.test"
    ;;
  production)
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

# Mapear variables específicas de ambiente a las generales que usa db_config.py
case "$ENV" in
  development)
    export DB_HOST="${DEV_DB_HOST:-localhost}"
    export DB_PORT="${DEV_DB_PORT:-5432}"
    export DB_NAME="${DEV_DB_NAME:-moneydiary_dev}"
    export DB_USER="${DEV_DB_USER:-postgres}"
    export DB_PASSWORD="${DEV_DB_PASS:-postgres}"
    export ENVIRONMENT="development"  # Para get_database_url
    ;;
  testing)
    export DB_HOST="${TEST_DB_HOST:-localhost}"
    export DB_PORT="${TEST_DB_PORT:-5432}"
    export DB_NAME="${TEST_DB_NAME:-moneydiary_test}"
    export DB_USER="${TEST_DB_USER:-postgres}"
    export DB_PASSWORD="${TEST_DB_PASS:-postgres}"
    export ENVIRONMENT="test"  # Para get_database_url
    ;;
  production)
    export DB_HOST="${PROD_DB_HOST:-localhost}"
    export DB_PORT="${PROD_DB_PORT:-5432}"
    export DB_NAME="${PROD_DB_NAME:-moneydiary}"
    export DB_USER="${PROD_DB_USER:-postgres}"
    export DB_PASSWORD="${PROD_DB_PASS:-postgres}"
    export ENVIRONMENT="production"  # Para get_database_url
    ;;
esac

# Verificar si necesitamos crear la base de datos (solo para comandos que lo requieran)
if [ "$COMMAND" = "upgrade" ] || [ "$COMMAND" = "revision" ] && [ "$ENV" != "production" ]; then
  # Preguntar antes de crear la base de datos en producción
  if [ "$ENV" = "production" ]; then
    read -p "¿Deseas crear la base de datos de producción si no existe? (s/N): " confirm
    if [[ "$confirm" =~ ^[Ss]$ ]]; then
      create_database_if_not_exists "$DB_HOST" "$DB_PORT" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"
    fi
  else
    # Crear automáticamente en entornos de desarrollo y pruebas
    create_database_if_not_exists "$DB_HOST" "$DB_PORT" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"
  fi
fi

# Construir argumentos para el script de migración
MIGRATE_ARGS="--env $ENV $COMMAND"

# Agregar opciones adicionales
while [ $# -gt 0 ]; do
  MIGRATE_ARGS="$MIGRATE_ARGS $1"
  shift
done

# Ejecutar el script de migración Python
echo "Ejecutando migración con ambiente $ENV: python migrate.py $MIGRATE_ARGS"
cd "$API_DIR" && python3 migrate.py $MIGRATE_ARGS
