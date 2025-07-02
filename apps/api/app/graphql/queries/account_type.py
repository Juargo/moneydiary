import strawberry
from strawberry.types import Info
from typing import List

from ..types.account_type import AccountType, convert_account_type_model_to_graphql
from ...services.account_type_service import get_all_account_types

def get_account_types(info: Info) -> List[AccountType]:
    """Obtiene todos los tipos de cuenta del sistema"""
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener los tipos de cuenta (SQLAlchemy models)
    account_type_models = get_all_account_types(db)
    
    # Convertir los modelos SQLAlchemy a tipos GraphQL
    account_types = [convert_account_type_model_to_graphql(model) for model in account_type_models]
    
    return account_types