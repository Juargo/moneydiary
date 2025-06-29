from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..models.accounts import Account

async def get_user_accounts(db: Session, user_id: int) -> List[Account]:
    """Obtiene todas las cuentas activas de un usuario"""
    result = await db.execute(
        select(Account).where(
            Account.user_id == user_id,
            Account.is_active == True
        )
    )
    return result.scalars().all()