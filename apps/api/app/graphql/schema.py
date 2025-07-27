import strawberry
from strawberry.types import Info
from typing import List, Optional
import logging

from ..version import __version__
from .types.description_pattern import (
    DescriptionPattern, 
    PatternTestResponse, 
    PatternSuggestionResponse,
    PatternTestInput,
    PatternSuggestionInput,
    PatternStatistics,
    DescriptionPatternCreateInput,
    DescriptionPatternUpdateInput
)

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
    from .queries.account import get_my_accounts, get_my_account
    logger.debug("✅ Account queries importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando account queries: {e}")
    # Crear resolver fallback
    @strawberry.field
    def get_my_accounts(info: Info) -> list:
        return []
    
    @strawberry.field
    def get_my_account(info: Info, account_id: int) -> None:
        return None

# Importar queries de bancos
try:
    from .queries.bank import get_banks
    logger.debug("✅ Bank queries importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando bank queries: {e}")
    # Crear resolver fallback
    @strawberry.field
    def get_banks(info: Info) -> list:
        return []

# Importar queries de tipos de cuenta
try:
    from .queries.account_type import get_account_types
    logger.debug("✅ AccountType queries importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando account_type queries: {e}")
    # Crear resolver fallback
    @strawberry.field
    def get_account_types(info: Info) -> list:
        return []

# Importar queries de transacciones
try:
    from .queries.transaction_simple import get_my_transactions, get_my_transaction
    logger.debug("✅ Transaction queries importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando transaction queries: {e}")
    # Crear resolver fallback
    @strawberry.field
    def get_my_transactions(info: Info) -> dict:
        return {"transactions": [], "total_count": 0}
    
    @strawberry.field
    def get_my_transaction(info: Info, transaction_id: int) -> None:
        return None

# Importar queries de patrones de descripción
try:
    from .queries.description_pattern import DescriptionPatternQueries
    description_pattern_queries = DescriptionPatternQueries()
    logger.debug("✅ Description pattern queries importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando description pattern queries: {e}")
    # Crear resolvers fallback
    @strawberry.field
    def my_description_patterns(info: Info) -> List[DescriptionPattern]:
        return []
    
    @strawberry.field
    def description_pattern(info: Info, pattern_id: int) -> Optional[DescriptionPattern]:
        return None
    
    @strawberry.field
    def test_description_patterns(info: Info, input: PatternTestInput) -> PatternTestResponse:
        return PatternTestResponse(description="", results=[], best_match=None)
    
    @strawberry.field
    def suggest_description_patterns(info: Info, input: PatternSuggestionInput) -> PatternSuggestionResponse:
        return PatternSuggestionResponse(suggestions=[])
    
    @strawberry.field
    def description_pattern_statistics(info: Info) -> PatternStatistics:
        return PatternStatistics(total_patterns=0, active_patterns=0, auto_apply_patterns=0, total_matches=0)

# Importar mutations de patrones de descripción
try:
    from .mutations.description_pattern import DescriptionPatternMutations
    description_pattern_mutations = DescriptionPatternMutations()
    logger.debug("✅ Description pattern mutations importadas correctamente")
except Exception as e:
    logger.error(f"❌ Error importando description pattern mutations: {e}")
    # Crear mutations fallback
    @strawberry.field
    def create_description_pattern(info: Info, input: DescriptionPatternCreateInput) -> Optional[DescriptionPattern]:
        return None
    
    @strawberry.field
    def update_description_pattern(info: Info, pattern_id: int, input: DescriptionPatternUpdateInput) -> Optional[DescriptionPattern]:
        return None
    
    @strawberry.field
    def delete_description_pattern(info: Info, pattern_id: int) -> bool:
        return False
    
    @strawberry.field
    def apply_pattern_to_transactions(info: Info, pattern_id: int, transaction_ids: Optional[List[int]] = None) -> int:
        return 0

@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return __version__

    @strawberry.field
    def hello(self) -> str:
        return "Hello from MoneyDiary API!"
    
    # Consultas de autenticación
    me = strawberry.field(resolver=get_me)
    google_auth_url = strawberry.field(resolver=get_google_auth_url)
    
    # Consultas de cuentas
    my_accounts = strawberry.field(resolver=get_my_accounts)
    my_account = strawberry.field(resolver=get_my_account)
    
    # Consultas de bancos
    banks = strawberry.field(resolver=get_banks)
    
    # Consultas de tipos de cuenta
    account_types = strawberry.field(resolver=get_account_types)
    
    # Consultas de transacciones
    my_transactions = strawberry.field(resolver=get_my_transactions)
    my_transaction = strawberry.field(resolver=get_my_transaction)
    
    # Consultas de patrones de descripción
    @strawberry.field
    async def my_description_patterns(
        self, 
        info: Info, 
        active_only: bool = True, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[DescriptionPattern]:
        """Obtener patrones del usuario actual"""
        try:
            return description_pattern_queries.my_description_patterns(
                info, active_only, skip, limit
            )
        except:
            return []
    
    @strawberry.field
    async def description_pattern(self, info: Info, pattern_id: int) -> Optional[DescriptionPattern]:
        """Obtener un patrón específico por ID"""
        try:
            return description_pattern_queries.description_pattern(info, pattern_id)
        except:
            return None
    
    @strawberry.field  
    async def test_description_patterns(self, info: Info, input: PatternTestInput) -> PatternTestResponse:
        """Probar patrones contra una descripción"""
        try:
            return description_pattern_queries.test_description_patterns(info, input)
        except:
            return PatternTestResponse(description="", results=[], best_match=None)
    
    @strawberry.field
    async def suggest_description_patterns(self, info: Info, input: PatternSuggestionInput) -> PatternSuggestionResponse:
        """Generar sugerencias de patrones"""
        try:
            return description_pattern_queries.suggest_description_patterns(info, input)
        except:
            return PatternSuggestionResponse(suggestions=[])
    
    @strawberry.field
    async def description_pattern_statistics(self, info: Info) -> PatternStatistics:
        """Obtener estadísticas de patrones"""
        try:
            return description_pattern_queries.description_pattern_statistics(info)
        except:
            return PatternStatistics(total_patterns=0, active_patterns=0, auto_apply_patterns=0, total_matches=0)

@strawberry.type
class Mutation:
    # Mutaciones de autenticación
    google_auth = strawberry.field(resolver=google_auth)
    refresh_token = strawberry.field(resolver=refresh_token)
    logout = strawberry.field(resolver=logout)
    
    # Mutaciones de patrones de descripción
    @strawberry.field
    async def create_description_pattern(self, info: Info, input: DescriptionPatternCreateInput) -> Optional[DescriptionPattern]:
        """Crear un nuevo patrón de descripción"""
        try:
            return description_pattern_mutations.create_description_pattern(info, input)
        except Exception as e:
            logger.error(f"Error creando patrón de descripción: {e}")
            return None
    
    @strawberry.field
    async def update_description_pattern(self, info: Info, pattern_id: int, input: DescriptionPatternUpdateInput) -> Optional[DescriptionPattern]:
        """Actualizar un patrón de descripción existente"""
        try:
            return description_pattern_mutations.update_description_pattern(info, pattern_id, input)
        except Exception as e:
            logger.error(f"Error actualizando patrón de descripción: {e}")
            return None
    
    @strawberry.field
    async def delete_description_pattern(self, info: Info, pattern_id: int) -> bool:
        """Eliminar un patrón de descripción"""
        try:
            return description_pattern_mutations.delete_description_pattern(info, pattern_id)
        except Exception as e:
            logger.error(f"Error eliminando patrón de descripción: {e}")
            return False
    
    @strawberry.field
    async def apply_pattern_to_transactions(
        self, 
        info: Info, 
        pattern_id: int, 
        transaction_ids: list[int] = None
    ) -> int:
        """Aplicar un patrón específico a transacciones retroactivamente"""
        try:
            return description_pattern_mutations.apply_pattern_to_transactions(
                info, pattern_id, transaction_ids
            )
        except Exception as e:
            logger.error(f"Error aplicando patrón a transacciones: {e}")
            return 0

# Crear schema con consultas y mutaciones
try:
    schema = strawberry.Schema(query=Query, mutation=Mutation)
    logger.info("✅ Schema GraphQL creado correctamente")
except Exception as e:
    logger.error(f"❌ Error creando schema GraphQL: {e}")
    raise