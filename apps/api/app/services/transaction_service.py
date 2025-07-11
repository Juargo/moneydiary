from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import csv
import io

from ..models.transactions import Transaction, TransactionStatus
from ..models.accounts import Account
from ..schemas.transactions import TransactionCreateRequest, TransactionUpdateRequest

def create_transaction(db: Session, user_id: int, transaction_data: TransactionCreateRequest) -> Transaction:
    """Crea una nueva transacción"""
    
    # Verificar que la cuenta pertenece al usuario
    account = db.query(Account).filter(
        Account.id == transaction_data.account_id,
        Account.user_id == user_id,
        Account.active == True
    ).first()
    
    if not account:
        raise ValueError("Cuenta no encontrada o no autorizada")
    
    # Si hay cuenta de transferencia, verificar que también pertenece al usuario
    if transaction_data.transfer_account_id:
        transfer_account = db.query(Account).filter(
            Account.id == transaction_data.transfer_account_id,
            Account.user_id == user_id,
            Account.active == True
        ).first()
        
        if not transfer_account:
            raise ValueError("Cuenta de transferencia no encontrada o no autorizada")
    
    # Crear la transacción
    db_transaction = Transaction(
        user_id=user_id,
        account_id=transaction_data.account_id,
        amount=Decimal(str(transaction_data.amount)),
        description=transaction_data.description,
        notes=transaction_data.notes,
        transaction_date=transaction_data.transaction_date,
        transfer_account_id=transaction_data.transfer_account_id,
        category_id=transaction_data.category_id,
        subcategory_id=transaction_data.subcategory_id,
        envelope_id=transaction_data.envelope_id,
        status_id=transaction_data.status_id,
        is_recurring=transaction_data.is_recurring,
        is_planned=transaction_data.is_planned,
        kakebo_emotion=transaction_data.kakebo_emotion,
        external_id=transaction_data.external_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_transaction)
    
    # Actualizar balance de la cuenta
    account.current_balance += Decimal(str(transaction_data.amount))
    
    # Si es transferencia, actualizar cuenta destino
    if transaction_data.transfer_account_id and transaction_data.amount < 0:
        transfer_account = db.query(Account).filter(Account.id == transaction_data.transfer_account_id).first()
        if transfer_account:
            transfer_account.current_balance += abs(Decimal(str(transaction_data.amount)))
    
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

def get_user_transactions(
    db: Session, 
    user_id: int,
    account_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Transaction]:
    """Obtiene las transacciones del usuario con filtros"""
    
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
    query = query.offset(skip).limit(limit)
    
    return query.all()

def get_user_transaction(db: Session, user_id: int, transaction_id: int) -> Optional[Transaction]:
    """Obtiene una transacción específica del usuario"""
    return db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()

def update_transaction(
    db: Session, 
    user_id: int, 
    transaction_id: int, 
    transaction_data: TransactionUpdateRequest
) -> Optional[Transaction]:
    """Actualiza una transacción existente"""
    
    # Obtener la transacción
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()
    
    if not db_transaction:
        return None
    
    # Guardar monto anterior para ajustar balances
    old_amount = db_transaction.amount
    old_account_id = db_transaction.account_id
    
    # Actualizar campos que no son None
    update_data = transaction_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(db_transaction, field):
            setattr(db_transaction, field, value)
    
    db_transaction.updated_at = datetime.utcnow()
    
    # Ajustar balances si cambió el monto o la cuenta
    if 'amount' in update_data or 'account_id' in update_data:
        # Revertir el monto anterior de la cuenta anterior
        old_account = db.query(Account).filter(Account.id == old_account_id).first()
        if old_account:
            old_account.current_balance -= old_amount
        
        # Aplicar nuevo monto a la cuenta (nueva o misma)
        new_account_id = update_data.get('account_id', old_account_id)
        new_amount = Decimal(str(update_data.get('amount', old_amount)))
        
        new_account = db.query(Account).filter(Account.id == new_account_id).first()
        if new_account:
            new_account.current_balance += new_amount
    
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

def delete_transaction(db: Session, user_id: int, transaction_id: int) -> bool:
    """Elimina una transacción"""
    
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()
    
    if not db_transaction:
        return False
    
    # Revertir el balance de la cuenta
    account = db.query(Account).filter(Account.id == db_transaction.account_id).first()
    if account:
        account.current_balance -= db_transaction.amount
    
    # Si era transferencia, revertir cuenta destino
    if db_transaction.transfer_account_id and db_transaction.amount < 0:
        transfer_account = db.query(Account).filter(Account.id == db_transaction.transfer_account_id).first()
        if transfer_account:
            transfer_account.current_balance -= abs(db_transaction.amount)
    
    db.delete(db_transaction)
    db.commit()
    
    return True

def import_transactions_from_csv(
    db: Session, 
    user_id: int, 
    account_id: int, 
    csv_content: str, 
    filename: str
) -> Dict[str, Any]:
    """Importa transacciones desde contenido CSV"""
    
    # Verificar que la cuenta pertenece al usuario
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == user_id,
        Account.active == True
    ).first()
    
    if not account:
        raise ValueError("Cuenta no encontrada o no autorizada")
    
    results = {
        'total_records': 0,
        'successful_imports': 0,
        'failed_imports': 0,
        'errors': []
    }
    
    try:
        # Leer CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start=2 porque row 1 es header
            results['total_records'] += 1
            
            try:
                # Mapear campos básicos (esto se puede mejorar con perfiles de importación)
                transaction_data = TransactionCreateRequest(
                    amount=float(row.get('amount', row.get('monto', '0'))),
                    description=row.get('description', row.get('descripcion', '')),
                    transaction_date=date.fromisoformat(row.get('date', row.get('fecha', ''))),
                    account_id=account_id,
                    notes=row.get('notes', row.get('notas', '')),
                )
                
                # Crear transacción
                create_transaction(db, user_id, transaction_data)
                results['successful_imports'] += 1
                
            except Exception as e:
                results['failed_imports'] += 1
                results['errors'].append(f"Fila {row_num}: {str(e)}")
                continue
                
    except Exception as e:
        raise ValueError(f"Error procesando CSV: {str(e)}")
    
    return results