"""
Seed para poblar la tabla category con entradas iniciales para los diferentes budgets.
"""
import logging
from tortoise import Tortoise
from app.db.models.budget import Budget
from app.db.models.category import Category

logger = logging.getLogger(__name__)

async def seed_categories():
    """
    Crea categorías iniciales para los diferentes presupuestos.
    
    Categorías para "Vida Personal": Work, Entretención, Subcripciones, Salud
    Categorías para "Imprevistos": Base
    Categorías para "Comisiones": Base
    Categorías para "Deudas": Tarjetas, Otros
    """
    try:
        # Definición de categorías por budget
        categories_by_budget = {
            "Vida Personal": [
                {"name": "Work", "description": "Gastos relacionados con el trabajo"},
                {"name": "Entretención", "description": "Gastos de ocio y entretenimiento"},
                {"name": "Subcripciones", "description": "Servicios de suscripción"},
                {"name": "Salud", "description": "Gastos médicos y bienestar"}
            ],
            "Imprevistos": [
                {"name": "Base", "description": "Gastos imprevistos generales"}
            ],
            "Comisiones": [
                {"name": "Base", "description": "Comisiones generales"}
            ],
            "Deudas": [
                {"name": "Tarjetas", "description": "Pagos de tarjetas de crédito"},
                {"name": "Otros", "description": "Otros tipos de deudas"}
            ]
        }
        
        # Procesar cada budget y sus categorías
        for budget_name, categories in categories_by_budget.items():
            # Obtener el budget
            budget = await Budget.get_or_none(name=budget_name)
            
            if not budget:
                logger.warning(f"Budget '{budget_name}' no encontrado. No se crearon sus categorías.")
                continue
                
            # Crear cada categoría para este budget
            for category_data in categories:
                existing_category = await Category.get_or_none(
                    name=category_data["name"],
                    budget=budget
                )
                
                if existing_category:
                    logger.info(f"Categoría '{category_data['name']}' ya existe para el budget '{budget_name}'")
                    continue
                    
                # Crear nueva categoría
                await Category.create(
                    budget=budget,
                    **category_data
                )
                logger.info(f"Categoría '{category_data['name']}' creada para el budget '{budget_name}'")
        
        logger.info("Seed de categorías completado con éxito")
        
    except Exception as e:
        logger.error(f"Error al crear las categorías: {str(e)}")


async def run():
    """
    Función principal para ejecutar el seed
    """
    await Tortoise.generate_schemas()
    await seed_categories()
    

if __name__ == "__main__":
    import asyncio
    from app.db.connection import init_db
    
    async def main():
        await init_db()
        await run()
        
    asyncio.run(main())
