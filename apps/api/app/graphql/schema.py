import strawberry
from strawberry.types import Info
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..version import __version__

# Importa los tipos de datos y resolvers específicos
from .types import (
    UserType,
    AccountType,
    # Otros tipos...
)

@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return __version__

    @strawberry.field
    def hello(self) -> str:
        return "Hello from MoneyDiary API!"
    
    # Agrega tus queries aquí
    # @strawberry.field
    # def users(self, info: Info) -> List[UserType]:
    #     db = next(get_db())
    #     # Implementa la lógica para obtener usuarios

@strawberry.type
class Mutation:
    # Agrega tus mutaciones aquí
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)