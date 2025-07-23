import strawberry
from strawberry.types import Info
from typing import Optional, List
from datetime import date
from decimal import Decimal
import logging

from ...services.transaction_service import get_user_transactions, get_user_transaction
from ...database import get_db

logger = logging.getLogger(__name__)

@strawberry.type
class Transaction:
    id: int
    amount: str
    description: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: date
    account_id: int
    user_id: int
    status_id: int
    is_recurring: bool = False
    is_planned: bool = False

@strawberry.type
class TransactionConnection:
    transactions: List[Transaction]
    total_count: int

@strawberry.input
class TransactionFilters:
    account_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

def get_my_transactions(
    info: Info,
    filters: Optional[TransactionFilters] = None,
    skip: int = 0,
    limit: int = 50
) -> TransactionConnection:
    """Obtiene las transacciones del usuario autenticado"""
    
    # Obtener usuario autenticado del contexto
    context = info.context
    if not hasattr(context, 'user') or context.user is None:
        raise Exception("Usuario no autenticado")
    
    current_user = context.user
    
    # Extraer user_id de manera segura
    if isinstance(current_user, dict):
        user_id_value = current_user.get('id')
    else:
        user_id_value = getattr(current_user, 'id', None)
    
    if user_id_value is None:
        raise Exception("ID de usuario no encontrado")
    
    try:
        user_id = int(user_id_value)
    except (ValueError, TypeError):
        raise Exception("ID de usuario no válido")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Preparar filtros
        account_id = None
        start_date = None
        end_date = None
        
        if filters:
            account_id = filters.account_id
            start_date = filters.start_date
            end_date = filters.end_date
        
        # Obtener transacciones usando el servicio
        transactions = get_user_transactions(
            db=db,
            user_id=user_id,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            subcategory_id=None,
            skip=skip,
            limit=limit
        )
        
        # Convertir a tipos GraphQL
        gql_transactions = []
        for db_transaction in transactions:
            gql_transactions.append(Transaction(
                id=db_transaction.id,
                amount=str(db_transaction.amount),
                description=db_transaction.description,
                notes=db_transaction.notes,
                transaction_date=db_transaction.transaction_date,
                account_id=db_transaction.account_id,
                user_id=db_transaction.user_id,
                status_id=db_transaction.status_id,
                is_recurring=db_transaction.is_recurring if db_transaction.is_recurring is not None else False,
                is_planned=db_transaction.is_planned if db_transaction.is_planned is not None else False
            ))
        
        logger.info(f"Transacciones obtenidas para usuario {user_id}: {len(gql_transactions)}")
        
        return TransactionConnection(
            transactions=gql_transactions,
            total_count=len(gql_transactions)
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo transacciones para usuario {user_id}: {str(e)}")
        raise Exception(f"Error obteniendo transacciones: {str(e)}")
    
    finally:
        db.close()

def get_my_transaction(info: Info, transaction_id: int) -> Optional[Transaction]:
    """Obtiene una transacción específica del usuario autenticado"""
    
    # Obtener usuario autenticado del contexto
    context = info.context
    if not hasattr(context, 'user') or context.user is None:
        raise Exception("Usuario no autenticado")
    
    current_user = context.user
    
    # Extraer user_id de manera segura
    if isinstance(current_user, dict):
        user_id_value = current_user.get('id')
    else:
        user_id_value = getattr(current_user, 'id', None)
    
    if user_id_value is None:
        raise Exception("ID de usuario no encontrado")
    
    try:
        user_id = int(user_id_value)
    except (ValueError, TypeError):
        raise Exception("ID de usuario no válido")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Obtener transacción usando el servicio
        transaction = get_user_transaction(
            db=db,
            user_id=user_id,
            transaction_id=transaction_id
        )
        
        if not transaction:
            return None
        
        return Transaction(
            id=transaction.id,
            amount=str(transaction.amount),
            description=transaction.description,
            notes=transaction.notes,
            transaction_date=transaction.transaction_date,
            account_id=transaction.account_id,
            user_id=transaction.user_id,
            status_id=transaction.status_id,
            is_recurring=transaction.is_recurring if transaction.is_recurring is not None else False,
            is_planned=transaction.is_planned if transaction.is_planned is not None else False
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo transacción {transaction_id} para usuario {user_id}: {str(e)}")
        raise Exception(f"Error obteniendo transacción: {str(e)}")
    
    finally:
        db.close()
