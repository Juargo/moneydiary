from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..models.account_types import AccountType

def get_all_account_types(db: Session) -> List[AccountType]:
    """Obtiene todos los tipos de cuenta del sistema"""
    try:
        result = db.execute(select(AccountType).order_by(AccountType.name))
        return result.scalars().all()
    except Exception as e:
        print(f"Error al obtener tipos de cuenta: {e}")
        return []