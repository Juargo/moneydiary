"""Ejecutar este archivo para poblar la base de datos con datos de prueba.
Importante: Primero debe ejecutarse schema_creator.py para crear la estructura de la base de datos"""

import asyncio
from tortoise import Tortoise
from app.db.config import TORTOISE_ORM
from app.db.seeds.banks import seed_banks
from app.db.seeds.users import seed_users
from app.db.seeds.user_banks import seed_user_banks
from app.db.seeds.budget_seed import seed_budgets
from app.db.seeds.category_seed import seed_categories
from app.db.seeds.subcategory_seed import seed_subcategories

async def run():
    """ Función para ejecutar los seeds """
    print("Inicializando conexión a la base de datos...")
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("Ejecutando seeds...")
    await seed_banks()
    await seed_users()
    await seed_user_banks()
    await seed_budgets()
    await seed_categories()
    await seed_subcategories()
    
    print("Seeds ejecutados exitosamente")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
