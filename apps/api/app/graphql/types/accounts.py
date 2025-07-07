import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class Account:
    id: int
    name: str
    account_type: str
    current_balance: float
    currency: str
    bank_id: Optional[int] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime
    account_number: float


def convert_account_model_to_graphql(account_model) -> Account:
    """Convert SQLAlchemy Account model to GraphQL Account type"""
    return Account(
        id=account_model.id,
        name=account_model.name,
        account_type=account_model.account_type.name if account_model.account_type else "Unknown",
        current_balance=account_model.current_balance,
        currency="CLP",  # Default currency, adjust based on your needs
        bank_id=account_model.bank_id,
        account_number=account_model.account_number,
        active=account_model.active,
        created_at=account_model.created_at,
        updated_at=account_model.updated_at
    )
