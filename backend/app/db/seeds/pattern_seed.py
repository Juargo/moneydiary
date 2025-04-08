"""
Seed para poblar la tabla pattern con entradas iniciales para todas las subcategorías.
"""
import logging
from tortoise import Tortoise
from app.db.models.subcategory import Subcategory
from app.db.models.pattern import Pattern

logger = logging.getLogger(__name__)

async def seed_patterns():
    """
    Crea patterns con expresión "baseexp" para todas las subcategorías existentes.
    """
    try:
        # Obtener todas las subcategorías
        subcategories = await Subcategory.all()
        
        if not subcategories:
            logger.warning("No se encontraron subcategorías. No se crearon patterns.")
            return
        
        # Recorrer todas las subcategorías y crear su pattern base
        for subcategory in subcategories:
            # Verificar si ya existe el pattern para esta subcategoría
            existing_pattern = await Pattern.get_or_none(
                match_text="baseexp",
                subcategory=subcategory
            )
            
            if existing_pattern:
                logger.info(f"Pattern 'baseexp' ya existe para la subcategoría '{subcategory.name}'")
                continue
            
            # Crear el pattern
            await Pattern.create(
                match_text="baseexp",
                subcategory=subcategory
            )
            logger.info(f"Pattern 'baseexp' creado para la subcategoría '{subcategory.name}'")
        
        logger.info("Seed de patterns completado con éxito")
        
    except Exception as e:
        logger.error(f"Error al crear los patterns: {str(e)}")


async def run():
    """
    Función principal para ejecutar el seed
    """
    await Tortoise.generate_schemas()
    await seed_patterns()
    

if __name__ == "__main__":
    import asyncio
    from app.db.connection import init_db
    
    async def main():
        await init_db()
        await run()
        
    asyncio.run(main())
