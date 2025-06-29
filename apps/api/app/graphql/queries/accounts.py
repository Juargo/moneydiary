import strawberry
from strawberry.types import Info
from typing import List

from ...crud.user import get_current_user
from ...models.accounts import Account
from ...services.account_service import get_user_accounts
from ..context import get_context

@strawberry.field
async def get_my_accounts(info: Info) -> List[Account]:
    """Obtiene todas las cuentas del usuario autenticado"""
    context = get_context(info)
    current_user = await get_current_user(context.db, context.token)
    
    if not current_user:
        raise Exception("Usuario no autenticado")
    
    accounts = await get_user_accounts(context.db, current_user.id)
    return accounts