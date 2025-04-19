# docker/dev.sh
#!/bin/bash
set -e

# Cargar variables de entorno para desarrollo
export $(grep -v '^#' docker/env/.env.dev | xargs)

# Ejecutar docker-compose con el archivo base y el de desarrollo
docker compose -f docker/compose/docker-compose.base.yml -f docker/compose/docker-compose.dev.yml "$@"