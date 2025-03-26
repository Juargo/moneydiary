""" Seed Banks """

from app.db.models import Bank

async def seed_banks():
    """ Seed Banks """
    banks_data = [
        {"name": "bancosantander", "description": "Banco Santander"},
        {"name": "bancoestado", "description": "Banco Estado"},
        {"name": "bancobci", "description": "BCI"},
        {"name": "bancofalabella", "description": "Banco Falabella"},
        {"name": "bancochile", "description": "Banco de Chile"},
    ]

    for bank in banks_data:
        await Bank.get_or_create(name=bank["name"], defaults={"description": bank["description"]})
        