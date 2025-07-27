from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..utils.fastapi_auth import get_current_user
from ..models.users import User
from ..services.description_pattern_service import DescriptionPatternService
from ..schemas.description_patterns import (
    DescriptionPatternCreate,
    DescriptionPatternUpdate,
    DescriptionPatternResponse,
    PatternTestRequest,
    PatternTestResponse,
    PatternSuggestionRequest,
    PatternSuggestionResponse
)

router = APIRouter(prefix="/description-patterns", tags=["description-patterns"])


@router.get("/", response_model=List[DescriptionPatternResponse])
async def get_my_description_patterns(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener los patrones de descripción del usuario actual"""
    patterns = DescriptionPatternService.get_user_patterns(
        db, current_user.id, active_only, skip, limit
    )
    
    # Convertir a response models
    response_patterns = []
    for pattern in patterns:
        from ..schemas.description_patterns import SubcategoryInfo
        
        subcategory_info = SubcategoryInfo(
            id=pattern.subcategory.id,
            name=pattern.subcategory.name,
            category_id=pattern.subcategory.category.id,
            category_name=pattern.subcategory.category.name
        )
        
        response_pattern = DescriptionPatternResponse(
            id=pattern.id,
            user_id=pattern.user_id,
            name=pattern.name,
            pattern=pattern.pattern,
            pattern_type=pattern.pattern_type,
            subcategory_id=pattern.subcategory_id,
            subcategory=subcategory_info,
            priority=pattern.priority,
            is_case_sensitive=pattern.is_case_sensitive,
            is_active=pattern.is_active,
            auto_apply=pattern.auto_apply,
            notes=pattern.notes,
            created_at=pattern.created_at,
            updated_at=pattern.updated_at
        )
        response_patterns.append(response_pattern)
    
    return response_patterns


@router.get("/{pattern_id}", response_model=DescriptionPatternResponse)
async def get_description_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener un patrón específico por ID"""
    pattern = DescriptionPatternService.get_pattern_by_id(db, current_user.id, pattern_id)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrón de descripción no encontrado"
        )
    
    from ..schemas.description_patterns import SubcategoryInfo
    
    subcategory_info = SubcategoryInfo(
        id=pattern.subcategory.id,
        name=pattern.subcategory.name,
        category_id=pattern.subcategory.category.id,
        category_name=pattern.subcategory.category.name
    )
    
    return DescriptionPatternResponse(
        id=pattern.id,
        user_id=pattern.user_id,
        name=pattern.name,
        pattern=pattern.pattern,
        pattern_type=pattern.pattern_type,
        subcategory_id=pattern.subcategory_id,
        subcategory=subcategory_info,
        priority=pattern.priority,
        is_case_sensitive=pattern.is_case_sensitive,
        is_active=pattern.is_active,
        auto_apply=pattern.auto_apply,
        notes=pattern.notes,
        created_at=pattern.created_at,
        updated_at=pattern.updated_at
    )


@router.post("/", response_model=DescriptionPatternResponse)
async def create_description_pattern(
    pattern_data: DescriptionPatternCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo patrón de descripción"""
    try:
        pattern = DescriptionPatternService.create_pattern(db, current_user.id, pattern_data)
        
        from ..schemas.description_patterns import SubcategoryInfo
        
        subcategory_info = SubcategoryInfo(
            id=pattern.subcategory.id,
            name=pattern.subcategory.name,
            category_id=pattern.subcategory.category.id,
            category_name=pattern.subcategory.category.name
        )
        
        return DescriptionPatternResponse(
            id=pattern.id,
            user_id=pattern.user_id,
            name=pattern.name,
            pattern=pattern.pattern,
            pattern_type=pattern.pattern_type,
            subcategory_id=pattern.subcategory_id,
            subcategory=subcategory_info,
            priority=pattern.priority,
            is_case_sensitive=pattern.is_case_sensitive,
            is_active=pattern.is_active,
            auto_apply=pattern.auto_apply,
            notes=pattern.notes,
            created_at=pattern.created_at,
            updated_at=pattern.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{pattern_id}", response_model=DescriptionPatternResponse)
async def update_description_pattern(
    pattern_id: int,
    pattern_data: DescriptionPatternUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar un patrón de descripción existente"""
    try:
        pattern = DescriptionPatternService.update_pattern(
            db, current_user.id, pattern_id, pattern_data
        )
        
        if not pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patrón de descripción no encontrado"
            )
        
        from ..schemas.description_patterns import SubcategoryInfo
        
        subcategory_info = SubcategoryInfo(
            id=pattern.subcategory.id,
            name=pattern.subcategory.name,
            category_id=pattern.subcategory.category.id,
            category_name=pattern.subcategory.category.name
        )
        
        return DescriptionPatternResponse(
            id=pattern.id,
            user_id=pattern.user_id,
            name=pattern.name,
            pattern=pattern.pattern,
            pattern_type=pattern.pattern_type,
            subcategory_id=pattern.subcategory_id,
            subcategory=subcategory_info,
            priority=pattern.priority,
            is_case_sensitive=pattern.is_active,
            is_active=pattern.is_active,
            auto_apply=pattern.auto_apply,
            notes=pattern.notes,
            created_at=pattern.created_at,
            updated_at=pattern.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{pattern_id}")
async def delete_description_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar un patrón de descripción"""
    success = DescriptionPatternService.delete_pattern(db, current_user.id, pattern_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrón de descripción no encontrado"
        )
    
    return {"message": "Patrón eliminado exitosamente"}


@router.post("/test", response_model=PatternTestResponse)
async def test_description_patterns(
    request: PatternTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Probar patrones contra una descripción"""
    return DescriptionPatternService.test_patterns(db, current_user.id, request)


@router.post("/suggestions", response_model=PatternSuggestionResponse)
async def suggest_description_patterns(
    request: PatternSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generar sugerencias de patrones basadas en transacciones existentes"""
    return DescriptionPatternService.generate_pattern_suggestions(db, current_user.id, request)


@router.get("/statistics/summary")
async def get_pattern_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de patrones del usuario"""
    return DescriptionPatternService.get_pattern_statistics(db, current_user.id)


@router.post("/{pattern_id}/apply")
async def apply_pattern_to_transactions(
    pattern_id: int,
    transaction_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aplicar un patrón específico a transacciones retroactivamente"""
    # Obtener el patrón
    pattern = DescriptionPatternService.get_pattern_by_id(db, current_user.id, pattern_id)
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrón no encontrado"
        )
    
    # Obtener transacciones objetivo
    from ..models.transactions import Transaction
    from ..models.recurring_patterns import PatternMatch
    from datetime import datetime
    
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.description.isnot(None)
    )
    
    if transaction_ids:
        query = query.filter(Transaction.id.in_(transaction_ids))
    
    transactions = query.all()
    
    applied_count = 0
    for transaction in transactions:
        desc = getattr(transaction, 'description', None)
        if desc and str(desc).strip():
            matched, matched_text = DescriptionPatternService.test_pattern_match(
                pattern, str(desc)
            )
            
            if matched:
                # Actualizar la transacción
                old_subcategory_id = getattr(transaction, 'subcategory_id', None)
                transaction.subcategory_id = pattern.subcategory_id
                
                # Registrar la coincidencia
                match_record = PatternMatch(
                    transaction_id=transaction.id,
                    pattern_id=pattern.id,
                    matched_text=matched_text,
                    applied_at=datetime.utcnow(),
                    was_manual_override=(old_subcategory_id is not None)
                )
                db.add(match_record)
                applied_count += 1
    
    db.commit()
    
    return {
        "message": f"Patrón aplicado a {applied_count} transacciones",
        "applied_count": applied_count
    }
