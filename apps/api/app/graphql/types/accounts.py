import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class AccountTypeType:  # Renamed to avoid clash with Python's type "type"
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime

@strawberry.type
class AccountType:
    id: int
    user_id: int
    account_type_id: int
    name: str
    current_balance: float
    is_tracking_only: bool
    include_in_net_worth: bool
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    # account_type: AccountTypeType = strawberry.field(resolver=get_account_type)
    # transactions: List["TransactionType"] = strawberry.field(resolver=get_account_transactions)