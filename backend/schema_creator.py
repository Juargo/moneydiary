"""Ejecutar este archivo para crear las tablas en la base de datos"""

import asyncio
from tortoise import Tortoise
from app.db.config import TORTOISE_ORM

async def create_schemas():
    """Función para crear la estructura de la base de datos"""
    print("Inicializando conexión a la base de datos...")
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("Generando esquemas...")
    await Tortoise.generate_schemas()
    
    print("Esquemas generados exitosamente")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(create_schemas())
