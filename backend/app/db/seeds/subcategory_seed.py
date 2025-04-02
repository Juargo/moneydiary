"""
Seed para poblar la tabla subcategory con entradas iniciales para todas las categorías.
"""
import logging
from tortoise import Tortoise
from app.db.models.category import Category
from app.db.models.subcategory import Subcategory

logger = logging.getLogger(__name__)

async def seed_subcategories():
    """
    Crea subcategorías "Base" para todas las categorías existentes.
    """
    try:
        # Obtener todas las categorías
        categories = await Category.all()
        
        if not categories:
            logger.warning("No se encontraron categorías. No se crearon subcategorías.")
            return
        
        # Recorrer todas las categorías y crear su subcategoría base
        for category in categories:
            # Verificar si ya existe la subcategoría Base para esta categoría
            existing_subcategory = await Subcategory.get_or_none(
                name="Base",
                category=category
            )
            
            if existing_subcategory:
                logger.info(f"Subcategoría 'Base' ya existe para la categoría '{category.name}'")
                continue
            
            # Crear la subcategoría Base
            await Subcategory.create(
                name="Base",
                description=f"Subcategoría base para {category.name}",
                amount=0,  # Valor inicial
                category=category
            )
            logger.info(f"Subcategoría 'Base' creada para la categoría '{category.name}'")
        
        logger.info("Seed de subcategorías completado con éxito")
        
    except Exception as e:
        logger.error(f"Error al crear las subcategorías: {str(e)}")


async def run():
    """
    Función principal para ejecutar el seed
    """
    await Tortoise.generate_schemas()
    await seed_subcategories()
    

if __name__ == "__main__":
    import asyncio
    from app.db.connection import init_db
    
    async def main():
        await init_db()
        await run()
        
    asyncio.run(main())
