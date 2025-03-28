""" Esquema de GraphQL """
from typing import List, Optional

import strawberry
from app.db.models.user import User as UserModel


@strawberry.type
class User:
    """ Tipo GraphQL para usuarios """
    id: int
    username: str
    # Cambiando los nombres de los campos para seguir la convención de camelCase de GraphQL
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class Query:
    """ Query type """
    @strawberry.field
    def hello(self) -> str:
        """ Hello world """
        return "Hola desde GraphQL 🚀"

    @strawberry.field
    async def user(self, user_id: int) -> Optional[User]:
        """ Obtener usuario por ID """
        user = await UserModel.get_or_none(id=user_id)
        if user:
            return User(
                id=user.id,
                username=user.username,
                created_at=str(user.created_at),
                updated_at=str(user.updated_at)
            )
        return None

    @strawberry.field
    async def users(self) -> List[User]:
        """ Obtener todos los usuarios """
        users = await UserModel.all()
        return [
            User(
                id=user.id,
                username=user.username,
                created_at=str(user.created_at),
                updated_at=str(user.updated_at)
            )
            for user in users
        ]

schema = strawberry.Schema(query=Query)
