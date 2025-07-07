from __future__ import annotations
import strawberry
from strawberry.types import Info
from typing import List, Optional

from ..types.accounts import Account, convert_account_model_to_graphql
from ...services.account_service import get_user_accounts, get_user_account_by_id
from ...utils.auth import get_authenticated_user

@strawberry.field
async def get_my_accounts(info: Info) -> List[Account]:
    """Obtiene todas las cuentas del usuario autenticado"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener las cuentas del usuario (SQLAlchemy models)
    account_models = get_user_accounts(db, current_user.id)
    
    # Convertir los modelos SQLAlchemy a tipos GraphQL
    accounts = [convert_account_model_to_graphql(model) for model in account_models]
    
    return accounts

@strawberry.field
async def get_my_account(info: Info, account_id: int) -> Optional[Account]:
    """Obtiene una cuenta específica del usuario autenticado por ID"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener la cuenta específica del usuario (SQLAlchemy model)
    account_model = get_user_account_by_id(db, current_user.id, account_id)
    
    if not account_model:
        return None
    
    # Convertir el modelo SQLAlchemy a tipo GraphQL
    return convert_account_model_to_graphql(account_model)