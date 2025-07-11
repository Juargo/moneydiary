from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import openpyxl
from openpyxl import load_workbook
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

def parse_excel_date(value):
    """Convierte diferentes formatos de fecha de Excel a date"""
    if value is None:
        return None
    
    # Si ya es un objeto datetime
    if isinstance(value, datetime):
        return value.date()
    
    # Si ya es un objeto date
    if isinstance(value, date):
        return value
    
    # Si es string, intentar parsear diferentes formatos
    if isinstance(value, str):
        date_formats = [
            '%Y-%m-%d',      # 2024-01-15
            '%d/%m/%Y',      # 15/01/2024
            '%d-%m-%Y',      # 15-01-2024
            '%m/%d/%Y',      # 01/15/2024
            '%d/%m/%y',      # 15/01/24
            '%Y%m%d',        # 20240115
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Formato de fecha no válido: {value}")
    
    # Si es un número (serial date de Excel)
    if isinstance(value, (int, float)):
        try:
            # Excel cuenta días desde 1900-01-01 (con ajuste por bug de año bisiesto)
            excel_epoch = datetime(1899, 12, 30)
            return (excel_epoch + timedelta(days=value)).date()
        except:
            raise ValueError(f"Fecha numérica no válida: {value}")
    
    raise ValueError(f"Tipo de fecha no soportado: {type(value)}")

def parse_excel_amount(value):
    """Convierte valores de Excel a float"""
    if value is None or value == '':
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Limpiar el string
        clean_value = value.strip().replace(',', '').replace('$', '').replace('€', '')
        
        # Manejar paréntesis como negativos (formato contable)
        if clean_value.startswith('(') and clean_value.endswith(')'):
            clean_value = '-' + clean_value[1:-1]
        
        try:
            return float(clean_value)
        except ValueError:
            raise ValueError(f"Monto no válido: {value}")
    
    raise ValueError(f"Tipo de monto no soportado: {type(value)}")

def detect_excel_columns(worksheet):
    """Detecta automáticamente las columnas en la primera fila"""
    header_row = 1
    headers = {}
    
    # Mapeo de posibles nombres de columnas
    column_mappings = {
        'date': ['date', 'fecha', 'día', 'dia', 'transaction_date', 'fecha_transaccion'],
        'amount': ['amount', 'monto', 'valor', 'importe', 'cantidad', 'sum', 'total'],
        'description': ['description', 'descripcion', 'concepto', 'detalle', 'memo', 'detail'],
        'notes': ['notes', 'notas', 'observaciones', 'comentarios', 'remarks']
    }
    
    # Leer la primera fila para encontrar headers
    for col_idx, cell in enumerate(worksheet[header_row], 1):
        if cell.value:
            cell_value = str(cell.value).lower().strip()
            
            # Buscar matches en los mapeos
            for field, possible_names in column_mappings.items():
                for possible_name in possible_names:
                    if possible_name in cell_value:
                        headers[field] = col_idx
                        break
                if field in headers:
                    break
    
    return headers, header_row

def import_transactions_from_excel(
    db: Session, 
    user_id: int, 
    account_id: int, 
    file_content: bytes, 
    filename: str
) -> Dict[str, Any]:
    """Importa transacciones desde contenido Excel"""
    
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
        # Cargar el workbook desde bytes
        workbook = load_workbook(io.BytesIO(file_content), read_only=True, data_only=True)
        
        # Usar la primera hoja
        worksheet = workbook.active
        
        # Detectar columnas automáticamente
        column_map, header_row = detect_excel_columns(worksheet)
        
        if not column_map.get('date') or not column_map.get('amount'):
            raise ValueError("No se pudieron detectar las columnas requeridas (fecha y monto). Verifica que el archivo tenga headers en la primera fila.")
        
        # Procesar filas
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=header_row + 1), start=header_row + 1):
            # Saltar filas vacías
            if all(cell.value is None or str(cell.value).strip() == '' for cell in row):
                continue
                
            results['total_records'] += 1
            
            try:
                # Extraer valores de las celdas
                date_value = row[column_map['date'] - 1].value if column_map.get('date') else None
                amount_value = row[column_map['amount'] - 1].value if column_map.get('amount') else None
                description_value = row[column_map['description'] - 1].value if column_map.get('description') else ""
                notes_value = row[column_map['notes'] - 1].value if column_map.get('notes') else ""
                
                # Validar y convertir valores
                transaction_date = parse_excel_date(date_value)
                amount = parse_excel_amount(amount_value)
                
                if transaction_date is None:
                    raise ValueError("Fecha requerida")
                
                if amount == 0:
                    raise ValueError("El monto no puede ser cero")
                
                # Crear transacción
                transaction_data = TransactionCreateRequest(
                    amount=amount,
                    description=str(description_value) if description_value else "",
                    transaction_date=transaction_date,
                    account_id=account_id,
                    notes=str(notes_value) if notes_value else "",
                    status_id=1  # Por defecto "completada"
                )
                
                create_transaction(db, user_id, transaction_data)
                results['successful_imports'] += 1
                
            except Exception as e:
                results['failed_imports'] += 1
                results['errors'].append(f"Fila {row_idx}: {str(e)}")
                continue
        
        workbook.close()
                
    except Exception as e:
        raise ValueError(f"Error procesando archivo Excel: {str(e)}")
    
    return results

# Mantener función legacy para CSV si es necesario
def import_transactions_from_csv(
    db: Session, 
    user_id: int, 
    account_id: int, 
    csv_content: str, 
    filename: str
) -> Dict[str, Any]:
    """Función legacy para CSV - redirige a Excel si el archivo es Excel"""
    if filename.lower().endswith(('.xlsx', '.xls')):
        raise ValueError("Use import_transactions_from_excel para archivos Excel")
    
    # Implementación CSV original...
    return import_transactions_from_excel(db, user_id, account_id, csv_content.encode(), filename)