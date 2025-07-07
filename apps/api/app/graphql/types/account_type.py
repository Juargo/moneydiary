from __future__ import annotations
import strawberry
from typing import Optional


@strawberry.type
class AccountType:
    id: int
    code: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


def convert_account_type_model_to_graphql(account_type_model) -> AccountType:
    """Convierte un modelo SQLAlchemy AccountType a tipo GraphQL AccountType"""
    return AccountType(
        id=account_type_model.id,
        code=account_type_model.code,
        name=account_type_model.name,
        description=account_type_model.description,
        created_at=account_type_model.created_at.isoformat() if account_type_model.created_at else None,
        updated_at=account_type_model.updated_at.isoformat() if account_type_model.updated_at else None
    )