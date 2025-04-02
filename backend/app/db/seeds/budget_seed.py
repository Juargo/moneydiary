"""
Seed para poblar la tabla budget con entradas iniciales para el usuario jorge.
"""
import logging
from tortoise import Tortoise
from app.db.models.user import User
from app.db.models.budget import Budget

logger = logging.getLogger(__name__)

async def seed_budgets():
    """
    Crea budgets iniciales para el usuario jorge.
    Categorías: Vida Personal, Comisiones, Deudas
    """
    try:
        # Buscar al usuario jorge
        jorge = await User.get_or_none(username="jorge")
        
        if not jorge:
            logger.warning("No se pudo encontrar al usuario 'jorge'. No se crearon budgets.")
            return
        
        # Definir los budgets a crear
        budgets_data = [
            {
                "name": "Vida Personal",
                "description": "Presupuesto para gastos personales y de ocio",
            },
            {
                "name": "Imprevistos",
                "description": "Presupuesto para gastos inesperados",
            },
            {
                "name": "Comisiones",
                "description": "Presupuesto para comisiones y gastos relacionados",
            },
            {
                "name": "Deudas",
                "description": "Presupuesto para el pago de deudas",
            }
        ]
        
        # Crear cada budget verificando si ya existe
        for budget_data in budgets_data:
            existing_budget = await Budget.get_or_none(
                user=jorge,
                name=budget_data["name"]
            )
            
            if existing_budget:
                logger.info(f"Budget '{budget_data['name']}' ya existe para el usuario jorge")
                continue
                
            # Crear nuevo budget
            await Budget.create(
                user=jorge,
                **budget_data
            )
            logger.info(f"Budget '{budget_data['name']}' creado para el usuario jorge")
            
        logger.info("Seed de budgets completado con éxito")
            
    except Exception as e:
        logger.error(f"Error al crear los budgets: {str(e)}")


async def run():
    """
    Función principal para ejecutar el seed
    """
    await Tortoise.generate_schemas()
    await seed_budgets()
    

if __name__ == "__main__":
    import asyncio
    from app.db.connection import init_db
    
    async def main():
        await init_db()
        await run()
        
    asyncio.run(main())
