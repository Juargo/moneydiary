from __future__ import annotations
import strawberry
from typing import Optional
from decimal import Decimal

from .bank import Bank, convert_bank_model_to_graphql
from .account_type import AccountType, convert_account_type_model_to_graphql


@strawberry.type
class Account:
    id: int
    name: str
    account_number: Optional[str] = None
    current_balance: Decimal
    active: bool
    user_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    bank: Bank
    account_type: AccountType


def convert_account_model_to_graphql(account_model) -> Account:
    """Convierte un modelo SQLAlchemy Account a tipo GraphQL Account"""
    return Account(
        id=account_model.id,
        name=account_model.name,
        account_number=account_model.account_number,
        current_balance=account_model.current_balance,
        active=account_model.active,
        user_id=account_model.user_id,
        created_at=account_model.created_at.isoformat() if account_model.created_at else None,
        updated_at=account_model.updated_at.isoformat() if account_model.updated_at else None,
        bank=convert_bank_model_to_graphql(account_model.bank),
        account_type=convert_account_type_model_to_graphql(account_model.account_type)
    )