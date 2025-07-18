from sqlalchemy.orm import Session
from sqlalchemy import update
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
    
    # Verificar que la cuenta existe y pertenece al usuario
    account = db.query(Account).filter(
        Account.id == profile_data.account_id,
        Account.user_id == user_id
    ).first()
    if not account:
        raise ValueError("Cuenta no encontrada o no pertenece al usuario")
    
    # Si se marca como default, desmarcar otros defaults del usuario para esta cuenta
    if profile_data.is_default:
        db.query(FileImportProfile).filter(
            FileImportProfile.user_id == user_id,
            FileImportProfile.account_id == profile_data.account_id,
            FileImportProfile.is_default == True
        ).update({FileImportProfile.is_default: False})
    
    # Crear el perfil
    db_profile = FileImportProfile(
        user_id=user_id,
        name=profile_data.name,
        description=profile_data.description,
        account_id=profile_data.account_id,
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
    account_id: Optional[int] = None
) -> List[FileImportProfile]:
    """Obtiene los perfiles de importación del usuario"""
    
    query = db.query(FileImportProfile).filter(FileImportProfile.user_id == user_id)
    
    if account_id:
        query = query.filter(FileImportProfile.account_id == account_id)
    
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
    
    # Si se marca como default, desmarcar otros defaults del usuario para esta cuenta
    if update_data.get('is_default') == True:
        db.query(FileImportProfile).filter(
            FileImportProfile.user_id == user_id,
            FileImportProfile.account_id == db_profile.account_id,
            FileImportProfile.id != profile_id,
            FileImportProfile.is_default == True
        ).update({FileImportProfile.is_default: False})
    
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    # Update timestamp directly in database
    db.execute(
        update(FileImportProfile)
        .where(FileImportProfile.id == profile_id)
        .values(updated_at=datetime.utcnow())
    )
    
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

def get_default_profile_for_account(
    db: Session, 
    user_id: int, 
    account_id: int
) -> Optional[FileImportProfile]:
    """Obtiene el perfil por defecto para una cuenta específica"""
    return db.query(FileImportProfile).filter(
        FileImportProfile.user_id == user_id,
        FileImportProfile.account_id == account_id,
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
        Account.name.label('account_name'),
        Bank.name.label('bank_name')
    ).join(
        FileImportProfile, FileImport.profile_id == FileImportProfile.id
    ).join(
        Account, FileImportProfile.account_id == Account.id
    ).join(
        Bank, Account.bank_id == Bank.id
    ).filter(
        FileImport.user_id == user_id
    ).order_by(
        FileImport.created_at.desc()
    ).offset(offset).limit(limit)
    
    results = []
    for import_record, profile_name, account_name, bank_name in query.all():
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
    # Esta función necesita ser refactorizada para trabajar con cuentas específicas
    # en lugar de bancos genéricos
    pass

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
        'bank_name': profile.account.bank.name if profile.account and profile.account.bank else None
    }