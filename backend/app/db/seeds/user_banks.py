""" Seed UserBank table """

from app.db.models import User, Bank, UserBank

async def seed_user_banks():
    """ Seed UserBank table """
    relations = [
        {"username": "jorge", "bank_name": "bancochile", "description": "Sueldo"},
        {"username": "jorge", "bank_name": "bancobci", "description": "Principal"},
        {"username": "jorge", "bank_name": "bancoestado", "description": "Transporte"},
        {"username": "jorge", "bank_name": "bancosantander", "description": "WorkCafe"},
        {"username": "matri", "bank_name": "bancobci", "description": "Matri"},
    ]

    for rel in relations:
        user = await User.get(username=rel["username"])
        bank = await Bank.get(name=rel["bank_name"])
        _, created = await UserBank.get_or_create(
            user=user,
            bank=bank,
            defaults={
                "description": rel["description"],
                "balance": 0.0
            }
        )
        if created:
            print(f"[✅] Relación creada: {user.username} → {bank.name} ({rel['description']})")
        else:
            print(f"[ℹ️] Relación ya existe: {user.username} → {bank.name}")
            