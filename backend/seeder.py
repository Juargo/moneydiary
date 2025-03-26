"""Ejecutar este archivo para crear las tablas en la base de datos y poblarlas 
con datos de prueba"""

import asyncio
from tortoise import Tortoise
from app.db.config import TORTOISE_ORM
from app.db.seeds.banks import seed_banks
from app.db.seeds.users import seed_users
from app.db.seeds.user_banks import seed_user_banks

async def run():
    """ Main function """
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await seed_banks()
    await seed_users()
    await seed_user_banks()
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
