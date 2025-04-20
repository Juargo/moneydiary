import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime
    
    # Relaciones serán implementadas más adelante
    # accounts: List["AccountType"] = strawberry.field(resolver=get_user_accounts)
    # default_financial_method: Optional["FinancialMethodType"]