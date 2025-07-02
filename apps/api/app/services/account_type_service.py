from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..models.account_types import AccountType

def get_all_account_types(db: Session) -> List[AccountType]:
    """Obtiene todos los tipos de cuenta del sistema"""
    result = db.execute(
        select(AccountType)
    )
    return result.scalars().unique().all()

