from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import openpyxl
from openpyxl import load_workbook
import io
import csv
import pandas as pd

from ..models.transactions import Transaction, TransactionStatus
from ..models.accounts import Account
from ..models.file_imports import FileImportProfile, FileColumnMapping
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

def import_transactions_with_profile(
    db: Session,
    user_id: int,
    profile_id: int,
    file_content: bytes,
    filename: str
) -> Dict[str, Any]:
    """Importa transacciones usando un perfil de importación configurado"""
    
    # Obtener el perfil de importación
    profile = db.query(FileImportProfile).filter(
        FileImportProfile.id == profile_id,
        FileImportProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise ValueError("Perfil de importación no encontrado")
    
    # Verificar que la cuenta pertenece al usuario
    account = db.query(Account).filter(
        Account.id == profile.account_id,
        Account.user_id == user_id,
        Account.active == True
    ).first()
    
    if not account:
        raise ValueError("Cuenta no encontrada o no autorizada")
    
    # Obtener los mapeos de columnas
    column_mappings = db.query(FileColumnMapping).filter(
        FileColumnMapping.profile_id == profile_id
    ).order_by(FileColumnMapping.position).all()
    
    if not column_mappings:
        raise ValueError("No se encontraron mapeos de columnas para el perfil")
    
    results = {
        'total_records': 0,
        'successful_imports': 0,
        'failed_imports': 0,
        'errors': []
    }
    
    try:
        # Determinar el tipo de archivo y procesarlo
        if filename.lower().endswith('.csv'):
            return _process_csv_with_profile(db, user_id, profile, column_mappings, file_content, results)
        elif filename.lower().endswith(('.xlsx', '.xls')):
            return _process_excel_with_profile(db, user_id, profile, column_mappings, file_content, results)
        else:
            raise ValueError("Tipo de archivo no soportado")
            
    except Exception as e:
        raise ValueError(f"Error procesando archivo: {str(e)}")

def _process_csv_with_profile(
    db: Session,
    user_id: int,
    profile: FileImportProfile,
    column_mappings: List[FileColumnMapping],
    file_content: bytes,
    results: Dict[str, Any]
) -> Dict[str, Any]:
    """Procesa un archivo CSV usando el perfil de importación"""
    
    try:
        # Decodificar el contenido
        encoding = getattr(profile, 'encoding', 'utf-8') or 'utf-8'
        csv_content = file_content.decode(encoding)
        
        # Crear un reader CSV
        delimiter = getattr(profile, 'delimiter', ',') or ','
        csv_reader = csv.reader(
            io.StringIO(csv_content),
            delimiter=delimiter
        )
        
        rows = list(csv_reader)
        
        # Saltar headers si existen
        has_header = getattr(profile, 'has_header', True)
        start_row = 1 if has_header else 0
        
        # Crear mapeo de columnas por nombre o índice
        column_map = {}
        for mapping in column_mappings:
            source_column_name = getattr(mapping, 'source_column_name', None)
            source_column_index = getattr(mapping, 'source_column_index', None)
            target_field_name = getattr(mapping, 'target_field_name', '')
            
            if has_header and source_column_name:
                # Buscar el índice de la columna por nombre
                try:
                    header_row = rows[0]
                    column_index = header_row.index(source_column_name)
                    column_map[target_field_name] = column_index
                except (IndexError, ValueError):
                    # Si no se encuentra, usar el índice configurado
                    if source_column_index is not None:
                        column_map[target_field_name] = source_column_index
            else:
                # Usar el índice configurado
                if source_column_index is not None:
                    column_map[target_field_name] = source_column_index
        
        # Procesar filas de datos
        for row_idx, row in enumerate(rows[start_row:], start=start_row + 1):
            if not row or all(not cell.strip() for cell in row):
                continue
                
            results['total_records'] += 1
            
            try:
                transaction_data = _extract_transaction_data(row, column_map, profile, row_idx)
                account_id = getattr(profile, 'account_id')
                transaction_data.account_id = account_id
                
                create_transaction(db, user_id, transaction_data)
                results['successful_imports'] += 1
                
            except Exception as e:
                results['failed_imports'] += 1
                results['errors'].append(f"Fila {row_idx}: {str(e)}")
                continue
                
    except Exception as e:
        raise ValueError(f"Error procesando CSV: {str(e)}")
    
    return results

def _process_excel_with_profile(
    db: Session,
    user_id: int,
    profile: FileImportProfile,
    column_mappings: List[FileColumnMapping],
    file_content: bytes,
    results: Dict[str, Any]
) -> Dict[str, Any]:
    """Procesa un archivo Excel usando el perfil de importación"""
    
    try:
        # Cargar el workbook
        workbook = load_workbook(io.BytesIO(file_content), read_only=True, data_only=True)
        
        # Seleccionar la hoja
        sheet_name = getattr(profile, 'sheet_name', None)
        if sheet_name:
            worksheet = workbook[sheet_name]
        else:
            worksheet = workbook.active
        
        # Crear mapeo de columnas
        column_map = {}
        has_header = getattr(profile, 'has_header', True)
        header_row_num = getattr(profile, 'header_row', 1)
        
        if has_header and header_row_num:
            # Leer la fila de headers
            header_row = list(worksheet.iter_rows(
                min_row=header_row_num,
                max_row=header_row_num,
                values_only=True
            ))[0]
            
            for mapping in column_mappings:
                source_column_name = getattr(mapping, 'source_column_name', None)
                source_column_index = getattr(mapping, 'source_column_index', None)
                target_field_name = getattr(mapping, 'target_field_name', '')
                
                if source_column_name:
                    try:
                        column_index = header_row.index(source_column_name)
                        column_map[target_field_name] = column_index
                    except ValueError:
                        if source_column_index is not None:
                            column_map[target_field_name] = source_column_index
                else:
                    if source_column_index is not None:
                        column_map[target_field_name] = source_column_index
        else:
            # Usar índices configurados
            for mapping in column_mappings:
                source_column_index = getattr(mapping, 'source_column_index', None)
                target_field_name = getattr(mapping, 'target_field_name', '')
                if source_column_index is not None:
                    column_map[target_field_name] = source_column_index
        
        # Procesar filas de datos
        start_row_num = getattr(profile, 'start_row', None)
        if start_row_num is None:
            start_row_num = header_row_num + 1 if header_row_num else 1
        
        skip_empty_rows = getattr(profile, 'skip_empty_rows', True)
        
        for row_idx, row in enumerate(worksheet.iter_rows(
            min_row=start_row_num,
            values_only=True
        ), start=start_row_num):
            
            if skip_empty_rows and (not row or all(cell is None or str(cell).strip() == '' for cell in row)):
                continue
                
            results['total_records'] += 1
            
            try:
                transaction_data = _extract_transaction_data(list(row), column_map, profile, row_idx)
                account_id = getattr(profile, 'account_id')
                transaction_data.account_id = account_id
                
                create_transaction(db, user_id, transaction_data)
                results['successful_imports'] += 1
                
            except Exception as e:
                results['failed_imports'] += 1
                results['errors'].append(f"Fila {row_idx}: {str(e)}")
                continue
        
        workbook.close()
        
    except Exception as e:
        raise ValueError(f"Error procesando Excel: {str(e)}")
    
    return results

def _extract_transaction_data(
    row: List,
    column_map: Dict[str, int],
    profile: FileImportProfile,
    row_idx: int
) -> TransactionCreateRequest:
    """Extrae los datos de transacción de una fila usando el mapeo de columnas"""
    
    def get_cell_value(field_name: str, default=None):
        if field_name in column_map and column_map[field_name] < len(row):
            value = row[column_map[field_name]]
            return value if value is not None else default
        return default
    
    # Extraer fecha
    date_value = get_cell_value('date')
    if not date_value:
        raise ValueError("Fecha requerida")
    
    transaction_date = parse_excel_date(date_value)
    if transaction_date is None:
        raise ValueError("Fecha inválida")
    
    # Extraer montos según el esquema configurado
    amount = 0.0
    amount_schema = getattr(profile, 'amount_schema')
    
    if hasattr(amount_schema, 'value'):
        schema_value = amount_schema.value
    else:
        schema_value = str(amount_schema)
    
    if schema_value == 'SINGLE_COLUMN':
        # Una sola columna con positivos/negativos
        amount_value = get_cell_value('amount', 0)
        amount = parse_excel_amount(amount_value)
        
        # Aplicar reglas de interpretación
        positive_is_income = getattr(profile, 'positive_is_income', True)
        if not positive_is_income:
            amount = -amount  # Invertir signo si positivo no es ingreso
            
    elif schema_value in ['SEPARATE_COLUMNS', 'DEBIT_CREDIT']:
        # Columnas separadas para débito/crédito
        debit_amount = parse_excel_amount(get_cell_value('debit_amount', 0))
        credit_amount = parse_excel_amount(get_cell_value('credit_amount', 0))
        
        # También soportar los nuevos campos expense_amount e income_amount
        expense_amount = parse_excel_amount(get_cell_value('expense_amount', 0))
        income_amount = parse_excel_amount(get_cell_value('income_amount', 0))
        
        debit_column_is_expense = getattr(profile, 'debit_column_is_expense', True)
        
        # Determinar el monto final
        if debit_amount != 0:
            amount = -abs(debit_amount) if debit_column_is_expense else abs(debit_amount)
        elif credit_amount != 0:
            amount = abs(credit_amount) if not debit_column_is_expense else -abs(credit_amount)
        elif expense_amount != 0:
            amount = -abs(expense_amount)  # Gastos siempre negativos
        elif income_amount != 0:
            amount = abs(income_amount)  # Ingresos siempre positivos
    
    if amount == 0:
        raise ValueError("El monto no puede ser cero")
    
    # Extraer otros campos
    description = str(get_cell_value('description', '')).strip()
    notes = str(get_cell_value('notes', '')).strip()
    
    return TransactionCreateRequest(
        amount=amount,
        description=description,
        transaction_date=transaction_date,
        account_id=0,  # Se asignará después
        notes=notes,
        status_id=1  # Por defecto "completada"
    )