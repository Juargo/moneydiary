from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List

from ..models.accounts import Account

def get_user_accounts(db: Session, user_id: int) -> List[Account]:
    """Obtiene todas las cuentas activas de un usuario"""
    # Load accounts with related account_type and bank data
    result = db.execute(
        select(Account)
        .options(
            joinedload(Account.account_type),
            joinedload(Account.bank)
        )
        .where(
            Account.user_id == user_id,
            Account.active == True
        )
    )
    return result.scalars().unique().all()
