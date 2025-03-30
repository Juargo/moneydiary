"""Database configuration"""

import os
from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv()

# Variables por defecto en caso de que no estén en .env
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DB", "moneydiary")

# Configuración para Tortoise ORM
TORTOISE_ORM = {
    "connections": {
        "default": (
            f"mysql://{DB_USER}:"
            f"{DB_PASSWORD}@"
            f"{DB_HOST}:"
            f"{DB_PORT}/"
            f"{DB_NAME}"
        )
    },
    "apps": {
        "models": {
            "models": ["app.db.models", "aerich.models"],
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
