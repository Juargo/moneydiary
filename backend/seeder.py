"""Ejecutar este archivo para crear las tablas en la base de datos y poblarlas 
con datos de prueba"""

import asyncio
from tortoise import Tortoise
from app.db.config import TORTOISE_ORM
from app.db.seeds.banks import seed_banks


async def run():
    """Crea las tablas en la base de datos y las pobla con datos de prueba"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()  # crea tablas si no existen
    await seed_banks()
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(run())
