import strawberry
from typing import Optional
from datetime import date

@strawberry.type
class SimpleTransaction:
    """Tipo simple de transacción para GraphQL"""
    id: int
    amount: str
    description: Optional[str] = None
    transaction_date: date
    account_id: int

@strawberry.type  
class SimpleTransactionList:
    """Lista simple de transacciones"""
    transactions: list[SimpleTransaction]
    count: int

def get_simple_transactions(info) -> SimpleTransactionList:
    """Resolver simple para transacciones"""
    return SimpleTransactionList(
        transactions=[],
        count=0
    )

def get_simple_transaction(info, transaction_id: int) -> Optional[SimpleTransaction]:
    """Resolver simple para una transacción"""
    return None
