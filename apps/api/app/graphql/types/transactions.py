
import strawberry
from typing import Optional, List
from datetime import datetime, date

@strawberry.type
class TransactionStatusType:
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

@strawberry.type
class TransactionType:
    id: int
    user_id: int
    account_id: int
    transfer_account_id: Optional[int]
    category_id: Optional[int]
    subcategory_id: Optional[int]
    envelope_id: Optional[int]
    status_id: int
    recurring_pattern_id: Optional[int]
    import_id: Optional[int]
    external_id: Optional[str]
    amount: float
    description: Optional[str]
    notes: Optional[str]
    transaction_date: date
    is_recurring: bool
    is_planned: bool
    kakebo_emotion: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    # account: AccountType = strawberry.field(resolver=get_transaction_account)
    # category: Optional[CategoryType] = strawberry.field(resolver=get_transaction_category)
    # status: TransactionStatusType = strawberry.field(resolver=get_transaction_status)