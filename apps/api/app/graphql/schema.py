import strawberry
from strawberry.types import Info
import logging

from ..version import __version__

logger = logging.getLogger(__name__)

# Importar todas las consultas y mutaciones con manejo de errores
try:
    from .queries.auth import get_me, get_google_auth_url
    logger.debug("✅ Auth queries importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando auth queries: {e}")
    # Crear resolvers fallback
    @strawberry.field
    def get_me(info: Info) -> str:
        return "User resolver not available"
    
    @strawberry.field  
    def get_google_auth_url(info: Info) -> str:
        return "Google auth not available"

try:
    from .mutations.auth import refresh_token, logout, google_auth
    logger.debug("✅ Auth mutations importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando auth mutations: {e}")
    # Crear mutations fallback
    @strawberry.field
    def refresh_token(info: Info) -> str:
        return "Refresh token not available"
    
    @strawberry.field
    def logout(info: Info) -> str:
        return "Logout not available"
    
    @strawberry.field
    def google_auth(info: Info) -> str:
        return "Google auth not available"

try:
    from .queries.account import get_my_accounts
    logger.debug("✅ Account queries importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando account queries: {e}")
    # Crear resolver fallback
    @strawberry.field
    def get_my_accounts(info: Info) -> list:
        return []

@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return __version__

    @strawberry.field
    def hello(self) -> str:
        return "Hello from MoneyDiary API!"
    
    # Consultas
    me = strawberry.field(resolver=get_me)
    google_auth_url = strawberry.field(resolver=get_google_auth_url)
    my_accounts = strawberry.field(resolver=get_my_accounts)

@strawberry.type
class Mutation:
    # Mutaciones de autenticación
    google_auth = strawberry.field(resolver=google_auth)
    refresh_token = strawberry.field(resolver=refresh_token)
    logout = strawberry.field(resolver=logout)

# Crear schema con manejo de errores
try:
    schema = strawberry.Schema(query=Query, mutation=Mutation)
    logger.info("✅ Schema GraphQL creado correctamente")
except Exception as e:
    logger.error(f"❌ Error creando schema GraphQL: {e}")
    raise