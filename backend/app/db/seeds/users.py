""" Seed users """

from app.db.models import User

async def seed_users():
    """ Seed users """
    users_data = [
        {"username": "jorge"},
        {"username": "matri"},
    ]

    for user in users_data:
        user_obj, created = await User.get_or_create(username=user["username"])
        if created:
            print(f"[✅] Usuario creado: {user_obj.username}")
        else:
            print(f"[ℹ️] Usuario ya existe: {user_obj.username}")
        