import strawberry
from strawberry.types import Info
from sqlalchemy.orm import Session

from ..database import get_db
from ..version import __version__

# Importar consultas y mutaciones de autenticación
from .queries.auth import get_me
from .mutations.auth import refresh_token, logout

@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return __version__

    @strawberry.field
    def hello(self) -> str:
        return "Hello from MoneyDiary API!"
    
    # Consulta para obtener el usuario autenticado actual
    me = strawberry.field(resolver=get_me)

@strawberry.type
class Mutation:
    # Mutaciones de autenticación
    refresh_token = strawberry.field(resolver=refresh_token)
    logout = strawberry.field(resolver=logout)

# Actualiza para incluir las mutaciones
schema = strawberry.Schema(query=Query, mutation=Mutation)