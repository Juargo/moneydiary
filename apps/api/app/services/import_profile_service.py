from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.file_imports import FileImportProfile, FileColumnMapping, FileImport
from ..models.banks import Bank
from ..models.accounts import Account
from ..schemas.file_imports import (
    FileImportProfileCreate, 
    FileImportProfileUpdate,
    FileColumnMappingCreate
)

def create_import_profile(
    db: Session, 
    user_id: int, 
    profile_data: FileImportProfileCreate
) -> FileImportProfile:
    """Crea un nuevo perfil de importación"""
    
    # Verificar que el banco existe
    bank = db.query(Bank).filter(Bank.id == profile_data.bank_id).first()
    if not bank:
        raise ValueError("Banco no encontrado")
    
    # Si se marca como default, desmarcar otros defaults del usuario para este banco
    if profile_data.is_default:
        db.query(FileImportProfile).filter(
            FileImportProfile.user_id == user_id,
            FileImportProfile.bank_id == profile_data.bank_id,
            FileImportProfile.is_default == True
        ).update({FileImportProfile.is_default: False})
    
    # Crear el perfil
    db_profile = FileImportProfile(
        user_id=user_id,
        name=profile_data.name,
        description=profile_data.description,
        bank_id=profile_data.bank_id,
        is_default=profile_data.is_default,
        delimiter=profile_data.delimiter,
        has_header=profile_data.has_header,
        date_format=profile_data.date_format,
        decimal_separator=profile_data.decimal_separator,
        encoding=profile_data.encoding,
        sheet_name=profile_data.sheet_name,
        header_row=profile_data.header_row,
        start_row=profile_data.start_row,
        skip_empty_rows=profile_data.skip_empty_rows,
        auto_detect_format=profile_data.auto_detect_format,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_profile)
    db.flush()  # Para obtener el ID
    
    # Crear mapeos de columnas
    for mapping_data in profile_data.column_mappings:
        db_mapping = FileColumnMapping(
            profile_id=db_profile.id,
            source_column_name=mapping_data.source_column_name,
            source_column_index=mapping_data.source_column_index,
            target_field_name=mapping_data.target_field_name,
            is_required=mapping_data.is_required,
            position=mapping_data.position,
            transformation_rule=mapping_data.transformation_rule,
            default_value=mapping_data.default_value,
            min_value=mapping_data.min_value,
            max_value=mapping_data.max_value,
            regex_pattern=mapping_data.regex_pattern,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_mapping)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

def get_user_import_profiles(
    db: Session, 
    user_id: int,
    bank_id: Optional[int] = None
) -> List[FileImportProfile]:
    """Obtiene los perfiles de importación del usuario"""
    
    query = db.query(FileImportProfile).filter(FileImportProfile.user_id == user_id)
    
    if bank_id:
        query = query.filter(FileImportProfile.bank_id == bank_id)
    
    return query.order_by(FileImportProfile.is_default.desc(), FileImportProfile.name).all()

def get_user_import_profile(
    db: Session, 
    user_id: int, 
    profile_id: int
) -> Optional[FileImportProfile]:
    """Obtiene un perfil específico del usuario"""
    return db.query(FileImportProfile).filter(
        FileImportProfile.id == profile_id,
        FileImportProfile.user_id == user_id
    ).first()

def update_import_profile(
    db: Session,
    user_id: int,
    profile_id: int,
    profile_data: FileImportProfileUpdate
) -> Optional[FileImportProfile]:
    """Actualiza un perfil de importación existente"""
    
    db_profile = get_user_import_profile(db, user_id, profile_id)
    if not db_profile:
        return None
    
    # Actualizar campos básicos
    update_data = profile_data.dict(exclude_unset=True, exclude={'column_mappings'})
    
    # Si se marca como default, desmarcar otros defaults del usuario para este banco
    if update_data.get('is_default') == True:
        db.query(FileImportProfile).filter(
            FileImportProfile.user_id == user_id,
            FileImportProfile.bank_id == db_profile.bank_id,
            FileImportProfile.id != profile_id,
            FileImportProfile.is_default == True
        ).update({FileImportProfile.is_default: False})
    
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db_profile.updated_at = datetime.utcnow()
    
    # Actualizar mapeos de columnas si se proporcionan
    if profile_data.column_mappings is not None:
        # Eliminar mapeos existentes
        db.query(FileColumnMapping).filter(
            FileColumnMapping.profile_id == profile_id
        ).delete()
        
        # Crear nuevos mapeos
        for mapping_data in profile_data.column_mappings:
            db_mapping = FileColumnMapping(
                profile_id=profile_id,
                source_column_name=mapping_data.source_column_name,
                source_column_index=mapping_data.source_column_index,
                target_field_name=mapping_data.target_field_name,
                is_required=mapping_data.is_required,
                position=mapping_data.position,
                transformation_rule=mapping_data.transformation_rule,
                default_value=mapping_data.default_value,
                min_value=mapping_data.min_value,
                max_value=mapping_data.max_value,
                regex_pattern=mapping_data.regex_pattern,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_mapping)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

def delete_import_profile(db: Session, user_id: int, profile_id: int) -> bool:
    """Elimina un perfil de importación"""
    
    db_profile = get_user_import_profile(db, user_id, profile_id)
    if not db_profile:
        return False
    
    # Verificar que no hay importaciones activas usando este perfil
    active_imports = db.query(FileImport).filter(
        FileImport.profile_id == profile_id,
        FileImport.status.in_(['pending', 'processing'])
    ).count()
    
    if active_imports > 0:
        raise ValueError("No se puede eliminar el perfil porque tiene importaciones activas")
    
    # Eliminar mapeos de columnas primero
    db.query(FileColumnMapping).filter(
        FileColumnMapping.profile_id == profile_id
    ).delete()
    
    # Eliminar el perfil
    db.delete(db_profile)
    db.commit()
    
    return True

def get_default_profile_for_bank(
    db: Session, 
    user_id: int, 
    bank_id: int
) -> Optional[FileImportProfile]:
    """Obtiene el perfil por defecto para un banco específico"""
    return db.query(FileImportProfile).filter(
        FileImportProfile.user_id == user_id,
        FileImportProfile.bank_id == bank_id,
        FileImportProfile.is_default == True
    ).first()

def get_import_history(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Obtiene el historial de importaciones del usuario"""
    
    query = db.query(
        FileImport,
        FileImportProfile.name.label('profile_name'),
        Bank.name.label('bank_name'),
        Account.name.label('account_name')
    ).join(
        FileImportProfile, FileImport.profile_id == FileImportProfile.id
    ).join(
        Bank, FileImportProfile.bank_id == Bank.id
    ).join(
        Account, FileImport.account_id == Account.id
    ).filter(
        FileImport.user_id == user_id
    ).order_by(
        FileImport.created_at.desc()
    ).offset(offset).limit(limit)
    
    results = []
    for import_record, profile_name, bank_name, account_name in query.all():
        results.append({
            'id': import_record.id,
            'filename': import_record.filename,
            'original_filename': import_record.original_filename,
            'file_type': import_record.file_type,
            'file_size': import_record.file_size,
            'record_count': import_record.record_count,
            'success_count': import_record.success_count,
            'error_count': import_record.error_count,
            'duplicate_count': import_record.duplicate_count,
            'status': import_record.status,
            'started_at': import_record.started_at,
            'completed_at': import_record.completed_at,
            'created_at': import_record.created_at,
            'profile_name': profile_name,
            'bank_name': bank_name,
            'account_name': account_name
        })
    
    return results

def create_default_profiles_for_popular_banks(db: Session, user_id: int):
    """Crea perfiles por defecto para bancos populares chilenos"""
    
    # Definir configuraciones por defecto para bancos populares
    default_configs = [
        {
            'bank_name': 'Banco de Chile',
            'profile_name': 'Estado de Cuenta Excel Estándar',
            'description': 'Formato estándar del estado de cuenta del Banco de Chile en Excel',
            'delimiter': ',',
            'date_format': 'DD/MM/YYYY',
            'decimal_separator': '.',
            'sheet_name': None,  # Primera hoja
            'header_row': 1,
            'start_row': 2,
            'mappings': [
                {'source': 'Fecha', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'Descripción', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'Monto', 'target': 'amount', 'required': True, 'position': 3},
                {'source': 'Referencia', 'target': 'reference', 'required': False, 'position': 4},
            ]
        },
        {
            'bank_name': 'Banco Santander',
            'profile_name': 'Cartola Santander Excel',
            'description': 'Formato estándar de cartola del Banco Santander en Excel',
            'delimiter': ';',
            'date_format': 'DD-MM-YYYY',
            'decimal_separator': ',',
            'sheet_name': 'Movimientos',
            'header_row': 3,  # A veces tienen encabezados en la fila 3
            'start_row': 4,
            'mappings': [
                {'source': 'FECHA', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'GLOSA', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'CARGO', 'target': 'amount', 'required': False, 'position': 3, 'transformation': 'negative'},
                {'source': 'ABONO', 'target': 'amount', 'required': False, 'position': 4, 'transformation': 'positive'},
                {'source': 'SALDO', 'target': 'notes', 'required': False, 'position': 5},
            ]
        },
        {
            'bank_name': 'BancoEstado',
            'profile_name': 'Estado de Cuenta BancoEstado Excel',
            'description': 'Formato estándar del BancoEstado en Excel',
            'delimiter': ',',
            'date_format': 'YYYY-MM-DD',
            'decimal_separator': '.',
            'sheet_name': None,
            'header_row': 1,
            'start_row': 2,
            'mappings': [
                {'source': 'fecha_contable', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'descripcion', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'monto', 'target': 'amount', 'required': True, 'position': 3},
                {'source': 'oficina', 'target': 'notes', 'required': False, 'position': 4},
            ]
        },
        {
            'bank_name': 'Banco de Crédito e Inversiones',
            'profile_name': 'Cartola BCI Excel',
            'description': 'Formato estándar de cartola del BCI en Excel',
            'delimiter': ',',
            'date_format': 'DD/MM/YYYY',
            'decimal_separator': '.',
            'sheet_name': None,
            'header_row': 1,
            'start_row': 2,
            'mappings': [
                {'source': 'Fecha', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'Detalle', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'Débito', 'target': 'amount', 'required': False, 'position': 3, 'transformation': 'negative'},
                {'source': 'Crédito', 'target': 'amount', 'required': False, 'position': 4, 'transformation': 'positive'},
                {'source': 'Número Documento', 'target': 'reference', 'required': False, 'position': 5},
            ]
        },
        {
            'bank_name': 'Banco Falabella',
            'profile_name': 'Estado de Cuenta Falabella Excel',
            'description': 'Formato estándar del Banco Falabella en Excel',
            'delimiter': ',',
            'date_format': 'DD/MM/YYYY',
            'decimal_separator': '.',
            'sheet_name': 'Movimientos',
            'header_row': 2,
            'start_row': 3,
            'mappings': [
                {'source': 'Fecha Mov.', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'Descripción', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'Monto', 'target': 'amount', 'required': True, 'position': 3},
                {'source': 'Documento', 'target': 'reference', 'required': False, 'position': 4},
            ]
        }
    ]
    
    for config in default_configs:
        # Buscar el banco
        bank = db.query(Bank).filter(Bank.name.ilike(f"%{config['bank_name']}%")).first()
        if not bank:
            continue
            
        # Verificar si ya existe un perfil por defecto para este banco
        existing = get_default_profile_for_bank(db, user_id, bank.id)
        if existing:
            continue
            
        # Crear el perfil
        try:
            mappings = [
                FileColumnMappingCreate(
                    source_column_name=m['source'],
                    target_field_name=m['target'],
                    is_required=m['required'],
                    position=m['position'],
                    transformation_rule=m.get('transformation')
                ) for m in config['mappings']
            ]
            
            profile_data = FileImportProfileCreate(
                name=config['profile_name'],
                description=config['description'],
                bank_id=bank.id,
                is_default=True,
                delimiter=config['delimiter'],
                date_format=config['date_format'],
                decimal_separator=config['decimal_separator'],
                sheet_name=config['sheet_name'],
                header_row=config['header_row'],
                start_row=config['start_row'],
                column_mappings=mappings
            )
            
            create_import_profile(db, user_id, profile_data)
            
        except Exception as e:
            print(f"Error creando perfil por defecto para {config['bank_name']}: {e}")
            continue

def validate_profile_for_import(
    db: Session,
    profile_id: int,
    user_id: int,
    file_type: str
) -> FileImportProfile:
    """Valida que un perfil sea adecuado para una importación específica"""
    
    profile = get_user_import_profile(db, user_id, profile_id)
    if not profile:
        raise ValueError("Perfil de importación no encontrado")
    
    # Validar que tenga mapeos requeridos
    mappings = {m.target_field_name: m for m in profile.column_mappings}
    
    if 'date' not in mappings:
        raise ValueError("El perfil debe tener un mapeo para el campo 'fecha'")
    
    if 'amount' not in mappings:
        raise ValueError("El perfil debe tener un mapeo para el campo 'monto'")
    
    # Validar mapeos requeridos
    required_mappings = [m for m in profile.column_mappings if m.is_required]
    if not required_mappings:
        raise ValueError("El perfil debe tener al menos un mapeo marcado como requerido")
    
    return profile

def get_profile_statistics(
    db: Session,
    user_id: int,
    profile_id: int
) -> Dict[str, Any]:
    """Obtiene estadísticas de uso de un perfil"""
    
    profile = get_user_import_profile(db, user_id, profile_id)
    if not profile:
        raise ValueError("Perfil no encontrado")
    
    # Contar importaciones
    total_imports = db.query(FileImport).filter(
        FileImport.profile_id == profile_id
    ).count()
    
    successful_imports = db.query(FileImport).filter(
        FileImport.profile_id == profile_id,
        FileImport.status == 'completed'
    ).count()
    
    failed_imports = db.query(FileImport).filter(
        FileImport.profile_id == profile_id,
        FileImport.status == 'failed'
    ).count()
    
    # Última importación
    last_import = db.query(FileImport).filter(
        FileImport.profile_id == profile_id
    ).order_by(FileImport.created_at.desc()).first()
    
    # Total de transacciones importadas
    total_transactions = db.query(FileImport.success_count).filter(
        FileImport.profile_id == profile_id,
        FileImport.status == 'completed'
    ).all()
    
    total_transaction_count = sum(count[0] or 0 for count in total_transactions)
    
    return {
        'profile_name': profile.name,
        'total_imports': total_imports,
        'successful_imports': successful_imports,
        'failed_imports': failed_imports,
        'success_rate': (successful_imports / total_imports * 100) if total_imports > 0 else 0,
        'total_transactions_imported': total_transaction_count,
        'last_import_date': last_import.created_at if last_import else None,
        'is_default': profile.is_default,
        'bank_name': profile.bank.name if profile.bank else None
    }