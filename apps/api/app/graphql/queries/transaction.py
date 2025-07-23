import strawberry
from strawberry.types import Info
from typing import Optional
from datetime import date
from decimal import Decimal
import logging

from ..types.transaction import Transaction, TransactionConnection, TransactionFilters
from ...services.transaction_service import get_user_transactions, get_user_transaction
from ...database import get_db

logger = logging.getLogger(__name__)

def get_my_transactions(
    info: Info,
    filters: Optional[TransactionFilters] = None,
    skip: int = 0,
    limit: int = 50
) -> TransactionConnection:
    """Obtiene las transacciones del usuario autenticado con filtros y paginación"""
    
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
        subcategory_id = None
        
        if filters:
            account_id = filters.account_id
            start_date = filters.start_date
            end_date = filters.end_date
            subcategory_id = filters.subcategory_id
        
        # Obtener transacciones usando el servicio
        transactions = get_user_transactions(
            db=db,
            user_id=user_id,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            subcategory_id=subcategory_id,
            skip=skip,
            limit=limit
        )
        
        # Aplicar filtros adicionales que no están en el servicio
        filtered_transactions = transactions
        if filters:
            if filters.min_amount:
                min_amount = Decimal(filters.min_amount)
                filtered_transactions = [t for t in filtered_transactions if Decimal(str(t.amount)) >= min_amount]
            
            if filters.max_amount:
                max_amount = Decimal(filters.max_amount)
                filtered_transactions = [t for t in filtered_transactions if Decimal(str(t.amount)) <= max_amount]
            
            if filters.description_contains:
                search_term = filters.description_contains.lower()
                filtered_transactions = [
                    t for t in filtered_transactions 
                    if t.description is not None and search_term in str(t.description).lower()
                ]
        
        # Convertir a tipos GraphQL
        gql_transactions = [Transaction.from_model(t) for t in filtered_transactions]
        
        # Calcular información de paginación
        total_count = len(filtered_transactions)
        has_next_page = len(transactions) == limit  # Si obtuvimos el límite completo, probablemente hay más
        has_previous_page = skip > 0
        
        logger.info(f"Transacciones obtenidas para usuario {user_id}: {len(gql_transactions)}")
        
        return TransactionConnection(
            transactions=gql_transactions,
            total_count=total_count,
            has_next_page=has_next_page,
            has_previous_page=has_previous_page
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
            logger.warning(f"Transacción {transaction_id} no encontrada para usuario {user_id}")
            return None
        
        logger.info(f"Transacción {transaction_id} obtenida para usuario {user_id}")
        return Transaction.from_model(transaction)
        
    except Exception as e:
        logger.error(f"Error obteniendo transacción {transaction_id} para usuario {user_id}: {str(e)}")
        raise Exception(f"Error obteniendo transacción: {str(e)}")
    
    finally:
        db.close()
