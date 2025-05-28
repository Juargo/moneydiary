import strawberry
from strawberry.types import Info

from ..version import __version__

# Importar todas las consultas y mutaciones
from .queries.auth import get_me, get_google_auth_url
from .mutations.auth import refresh_token, logout, google_auth

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
    google_auth_url = strawberry.field(resolver=get_google_auth_url)

@strawberry.type
class Mutation:
    # Mutaciones de autenticación
    google_auth = strawberry.field(resolver=google_auth)
    refresh_token = strawberry.field(resolver=refresh_token)
    logout = strawberry.field(resolver=logout)

# Crear schema con consultas y mutaciones
schema = strawberry.Schema(query=Query, mutation=Mutation)