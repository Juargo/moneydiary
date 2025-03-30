"""Database configuration"""

import os
import logging
from dotenv import load_dotenv
from tortoise import Tortoise
from urllib.parse import quote_plus

# Cargar variables de ambiente desde .env si existe
load_dotenv()

logger = logging.getLogger(__name__)

# Determinar si estamos en modo desarrollo o producción
ENV = os.getenv("ENV", "development")

# Leer variables de ambiente
DB_HOST = os.getenv("MYSQL_HOST", "mysql" if ENV == "development" else "localhost")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DB", "moneydiary_db")
DB_USER = os.getenv("MYSQL_USER", "moneydiary_user")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "moneydiary_password")

# Construir URL de conexión
DATABASE_URL = f"mysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Log de configuración (sin información sensible)
logger.info(f"Configurando conexión a base de datos en entorno: {ENV}")
logger.info(f"Host: {DB_HOST}, Puerto: {DB_PORT}, Base de datos: {DB_NAME}")

# Configuración para Tortoise ORM
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    # Agregar esta opción para evitar advertencias de recreación de tablas
    "use_tz": False,
    "timezone": "UTC"
}

# Función para inicializar Tortoise ORM manualmente
async def init_db(create_schemas=False):
    """Initialize the database connection.
    
    Args:
        create_schemas: If True, create database schemas.
    """
    await Tortoise.init(config=TORTOISE_ORM)
    if create_schemas:
        # Solo generar esquemas si explícitamente se solicita
        await Tortoise.generate_schemas()

async def close_db():
    """Close database connections."""
    await Tortoise.close_connections()
