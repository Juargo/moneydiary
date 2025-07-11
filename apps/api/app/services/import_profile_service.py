from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.csv_imports import CsvImportProfile, CsvColumnMapping, CsvImport
from ..models.banks import Bank
from ..schemas.import_profiles import (
    CsvImportProfileCreate, 
    CsvImportProfileUpdate,
    CsvColumnMappingCreate
)

def create_import_profile(
    db: Session, 
    user_id: int, 
    profile_data: CsvImportProfileCreate
) -> CsvImportProfile:
    """Crea un nuevo perfil de importación"""
    
    # Verificar que el banco existe
    bank = db.query(Bank).filter(Bank.id == profile_data.bank_id).first()
    if not bank:
        raise ValueError("Banco no encontrado")
    
    # Si se marca como default, desmarcar otros defaults del usuario para este banco
    if profile_data.is_default:
        db.query(CsvImportProfile).filter(
            CsvImportProfile.user_id == user_id,
            CsvImportProfile.bank_id == profile_data.bank_id,
            CsvImportProfile.is_default == True
        ).update({CsvImportProfile.is_default: False})
    
    # Crear el perfil
    db_profile = CsvImportProfile(
        user_id=user_id,
        name=profile_data.name,
        description=profile_data.description,
        bank_id=profile_data.bank_id,
        is_default=profile_data.is_default,
        delimiter=profile_data.delimiter,
        has_header=profile_data.has_header,
        date_format=profile_data.date_format,
        decimal_separator=profile_data.decimal_separator,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_profile)
    db.flush()  # Para obtener el ID
    
    # Crear mapeos de columnas
    for mapping_data in profile_data.column_mappings:
        db_mapping = CsvColumnMapping(
            profile_id=db_profile.id,
            source_column_name=mapping_data.source_column_name,
            target_field_name=mapping_data.target_field_name,
            is_required=mapping_data.is_required,
            position=mapping_data.position,
            transformation_rule=mapping_data.transformation_rule,
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
) -> List[CsvImportProfile]:
    """Obtiene los perfiles de importación del usuario"""
    
    query = db.query(CsvImportProfile).filter(CsvImportProfile.user_id == user_id)
    
    if bank_id:
        query = query.filter(CsvImportProfile.bank_id == bank_id)
    
    return query.order_by(CsvImportProfile.is_default.desc(), CsvImportProfile.name).all()

def get_user_import_profile(
    db: Session, 
    user_id: int, 
    profile_id: int
) -> Optional[CsvImportProfile]:
    """Obtiene un perfil específico del usuario"""
    return db.query(CsvImportProfile).filter(
        CsvImportProfile.id == profile_id,
        CsvImportProfile.user_id == user_id
    ).first()

def update_import_profile(
    db: Session,
    user_id: int,
    profile_id: int,
    profile_data: CsvImportProfileUpdate
) -> Optional[CsvImportProfile]:
    """Actualiza un perfil de importación existente"""
    
    db_profile = get_user_import_profile(db, user_id, profile_id)
    if not db_profile:
        return None
    
    # Actualizar campos básicos
    update_data = profile_data.dict(exclude_unset=True, exclude={'column_mappings'})
    
    # Si se marca como default, desmarcar otros defaults del usuario para este banco
    if update_data.get('is_default') == True:
        db.query(CsvImportProfile).filter(
            CsvImportProfile.user_id == user_id,
            CsvImportProfile.bank_id == db_profile.bank_id,
            CsvImportProfile.id != profile_id,
            CsvImportProfile.is_default == True
        ).update({CsvImportProfile.is_default: False})
    
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db_profile.updated_at = datetime.utcnow()
    
    # Actualizar mapeos de columnas si se proporcionan
    if profile_data.column_mappings is not None:
        # Eliminar mapeos existentes
        db.query(CsvColumnMapping).filter(
            CsvColumnMapping.profile_id == profile_id
        ).delete()
        
        # Crear nuevos mapeos
        for mapping_data in profile_data.column_mappings:
            db_mapping = CsvColumnMapping(
                profile_id=profile_id,
                source_column_name=mapping_data.source_column_name,
                target_field_name=mapping_data.target_field_name,
                is_required=mapping_data.is_required,
                position=mapping_data.position,
                transformation_rule=mapping_data.transformation_rule,
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
    
    # Eliminar mapeos de columnas primero
    db.query(CsvColumnMapping).filter(
        CsvColumnMapping.profile_id == profile_id
    ).delete()
    
    # Eliminar el perfil
    db.delete(db_profile)
    db.commit()
    
    return True

def get_default_profile_for_bank(
    db: Session, 
    user_id: int, 
    bank_id: int
) -> Optional[CsvImportProfile]:
    """Obtiene el perfil por defecto para un banco específico"""
    return db.query(CsvImportProfile).filter(
        CsvImportProfile.user_id == user_id,
        CsvImportProfile.bank_id == bank_id,
        CsvImportProfile.is_default == True
    ).first()

def get_import_history(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Obtiene el historial de importaciones del usuario"""
    
    query = db.query(
        CsvImport,
        CsvImportProfile.name.label('profile_name'),
        Bank.name.label('bank_name')
    ).join(
        CsvImportProfile, CsvImport.profile_id == CsvImportProfile.id
    ).join(
        Bank, CsvImportProfile.bank_id == Bank.id
    ).filter(
        CsvImport.user_id == user_id
    ).order_by(
        CsvImport.created_at.desc()
    ).offset(offset).limit(limit)
    
    results = []
    for import_record, profile_name, bank_name in query.all():
        results.append({
            'id': import_record.id,
            'filename': import_record.filename,
            'original_filename': import_record.original_filename,
            'record_count': import_record.record_count,
            'success_count': import_record.success_count,
            'error_count': import_record.error_count,
            'duplicate_count': import_record.duplicate_count,
            'status': import_record.status,
            'started_at': import_record.started_at,
            'completed_at': import_record.completed_at,
            'created_at': import_record.created_at,
            'profile_name': profile_name,
            'bank_name': bank_name
        })
    
    return results

def create_default_profiles_for_popular_banks(db: Session, user_id: int):
    """Crea perfiles por defecto para bancos populares chilenos"""
    
    # Definir configuraciones por defecto para bancos populares
    default_configs = [
        {
            'bank_name': 'Banco de Chile',
            'profile_name': 'Estado de Cuenta Estándar',
            'description': 'Formato estándar del estado de cuenta del Banco de Chile',
            'delimiter': ',',
            'date_format': 'DD/MM/YYYY',
            'mappings': [
                {'source': 'Fecha', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'Descripcion', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'Monto', 'target': 'amount', 'required': True, 'position': 3},
                {'source': 'Referencia', 'target': 'reference', 'required': False, 'position': 4},
            ]
        },
        {
            'bank_name': 'Banco Santander',
            'profile_name': 'Cartola Santander',
            'description': 'Formato estándar de cartola del Banco Santander',
            'delimiter': ';',
            'date_format': 'DD-MM-YYYY',
            'mappings': [
                {'source': 'FECHA', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'GLOSA', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'CARGO', 'target': 'amount', 'required': False, 'position': 3, 'transformation': 'negative'},
                {'source': 'ABONO', 'target': 'amount', 'required': False, 'position': 4, 'transformation': 'positive'},
            ]
        },
        {
            'bank_name': 'BancoEstado',
            'profile_name': 'Estado de Cuenta BancoEstado',
            'description': 'Formato estándar del BancoEstado',
            'delimiter': ',',
            'date_format': 'YYYY-MM-DD',
            'mappings': [
                {'source': 'fecha_contable', 'target': 'date', 'required': True, 'position': 1},
                {'source': 'descripcion', 'target': 'description', 'required': True, 'position': 2},
                {'source': 'monto', 'target': 'amount', 'required': True, 'position': 3},
                {'source': 'oficina', 'target': 'notes', 'required': False, 'position': 4},
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
                CsvColumnMappingCreate(
                    source_column_name=m['source'],
                    target_field_name=m['target'],
                    is_required=m['required'],
                    position=m['position'],
                    transformation_rule=m.get('transformation')
                ) for m in config['mappings']
            ]
            
            profile_data = CsvImportProfileCreate(
                name=config['profile_name'],
                description=config['description'],
                bank_id=bank.id,
                is_default=True,
                delimiter=config['delimiter'],
                date_format=config['date_format'],
                column_mappings=mappings
            )
            
            create_import_profile(db, user_id, profile_data)
            
        except Exception as e:
            print(f"Error creando perfil por defecto para {config['bank_name']}: {e}")
            continue