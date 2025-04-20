import strawberry
from strawberry.types import Info
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..version import __version__

# Importamos todos los tipos
from .types import (
    UserType,
    AccountType,
    AccountTypeType,
    CategoryGroupType,
    CategoryType,
    SubcategoryType,
    FinancialMethodType,
    TransactionType,
    TransactionStatusType
    # Otros tipos según se vayan implementando
)

@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return __version__

    @strawberry.field
    def hello(self) -> str:
        return "Hello from MoneyDiary API!"
    
    # Ejemplo básico de query
    # @strawberry.field
    # def users(self, info: Info) -> List[UserType]:
    #     db = next(get_db())
    #     # Implementa la lógica para obtener usuarios
    #     return []

@strawberry.type
class Mutation:
    # Las mutaciones se implementarán más adelante
    pass

# schema = strawberry.Schema(query=Query, mutation=Mutation)
schema = strawberry.Schema(query=Query)