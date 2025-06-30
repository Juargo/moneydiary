from __future__ import annotations
import strawberry
from typing import List, TYPE_CHECKING

from ..types.accounts import Account, convert_account_model_to_graphql
from ...services.account_service import get_user_accounts
from ...utils.auth import get_authenticated_user

if TYPE_CHECKING:
    from strawberry.types import Info

async def get_my_accounts(root, info: "Info") -> List[Account]:
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
