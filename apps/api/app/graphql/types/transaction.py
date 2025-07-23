import strawberry
from typing import Optional, List
from datetime import date
from decimal import Decimal

from ...models.transactions import Transaction as TransactionModel

@strawberry.type
class TransactionStatus:
    id: int
    name: str
    description: Optional[str] = None

@strawberry.type  
class Transaction:
    id: int
    user_id: int
    account_id: int
    transfer_account_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    envelope_id: Optional[int] = None
    status_id: int
    recurring_pattern_id: Optional[int] = None
    import_id: Optional[int] = None
    import_row_number: Optional[int] = None
    external_id: Optional[str] = None
    amount: str  # Usamos string para manejar Decimal correctamente
    description: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: date
    is_recurring: bool
    is_planned: bool
    kakebo_emotion: Optional[str] = None
    
    @classmethod
    def from_model(cls, transaction: TransactionModel) -> "Transaction":
        """Convierte un modelo de Transaction a tipo GraphQL"""
        return cls(
            id=transaction.id,
            user_id=transaction.user_id,
            account_id=transaction.account_id,
            transfer_account_id=transaction.transfer_account_id,
            subcategory_id=transaction.subcategory_id,
            envelope_id=transaction.envelope_id,
            status_id=transaction.status_id,
            recurring_pattern_id=transaction.recurring_pattern_id,
            import_id=transaction.import_id,
            import_row_number=transaction.import_row_number,
            external_id=transaction.external_id,
            amount=str(transaction.amount),  # Convertir Decimal a string
            description=transaction.description,
            notes=transaction.notes,
            transaction_date=transaction.transaction_date,
            is_recurring=transaction.is_recurring,
            is_planned=transaction.is_planned,
            kakebo_emotion=transaction.kakebo_emotion
        )

@strawberry.type
class TransactionConnection:
    """Paginación de transacciones"""
    transactions: List[Transaction]
    total_count: int
    has_next_page: bool
    has_previous_page: bool

@strawberry.input
class TransactionFilters:
    """Filtros para consultar transacciones"""
    account_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    subcategory_id: Optional[int] = None
    min_amount: Optional[str] = None
    max_amount: Optional[str] = None
    description_contains: Optional[str] = None
