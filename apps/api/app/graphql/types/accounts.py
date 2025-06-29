import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class Account:
    id: int
    name: str
    account_type: str
    balance: float
    currency: str
    bank_id: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime