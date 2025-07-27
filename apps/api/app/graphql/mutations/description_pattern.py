import strawberry
from typing import Optional
from sqlalchemy.orm import Session
from strawberry.types import Info

from ..types.description_pattern import (
    DescriptionPattern,
    DescriptionPatternCreateInput,
    DescriptionPatternUpdateInput
)
from ...services.description_pattern_service import DescriptionPatternService
from ...schemas.description_patterns import (
    DescriptionPatternCreate,
    DescriptionPatternUpdate,
    PatternType as SchemaPatternType
)
from ..queries.description_pattern import convert_db_pattern_to_graphql


@strawberry.type
class DescriptionPatternMutations:
    
    @strawberry.mutation
    def create_description_pattern(
        self,
        info: Info,
        input: DescriptionPatternCreateInput
    ) -> DescriptionPattern:
        """Crear un nuevo patrón de descripción"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        # Convertir input GraphQL a esquema Pydantic
        pattern_data = DescriptionPatternCreate(
            name=input.name,
            pattern=input.pattern,
            pattern_type=SchemaPatternType(input.pattern_type.value),
            subcategory_id=input.subcategory_id,
            priority=input.priority,
            is_case_sensitive=input.is_case_sensitive,
            is_active=input.is_active,
            auto_apply=input.auto_apply,
            notes=input.notes
        )
        
        db_pattern = DescriptionPatternService.create_pattern(db, user_id, pattern_data)
        
        return convert_db_pattern_to_graphql(db_pattern)
    
    @strawberry.mutation
    def update_description_pattern(
        self,
        info: Info,
        pattern_id: int,
        input: DescriptionPatternUpdateInput
    ) -> Optional[DescriptionPattern]:
        """Actualizar un patrón de descripción existente"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        # Convertir input GraphQL a esquema Pydantic
        update_data = {}
        if input.name is not None:
            update_data['name'] = input.name
        if input.pattern is not None:
            update_data['pattern'] = input.pattern
        if input.pattern_type is not None:
            update_data['pattern_type'] = SchemaPatternType(input.pattern_type.value)
        if input.subcategory_id is not None:
            update_data['subcategory_id'] = input.subcategory_id
        if input.priority is not None:
            update_data['priority'] = input.priority
        if input.is_case_sensitive is not None:
            update_data['is_case_sensitive'] = input.is_case_sensitive
        if input.is_active is not None:
            update_data['is_active'] = input.is_active
        if input.auto_apply is not None:
            update_data['auto_apply'] = input.auto_apply
        if input.notes is not None:
            update_data['notes'] = input.notes
            
        pattern_update = DescriptionPatternUpdate(**update_data)
        
        db_pattern = DescriptionPatternService.update_pattern(db, user_id, pattern_id, pattern_update)
        
        if db_pattern:
            return convert_db_pattern_to_graphql(db_pattern)
        return None
    
    @strawberry.mutation
    def delete_description_pattern(
        self,
        info: Info,
        pattern_id: int
    ) -> bool:
        """Eliminar un patrón de descripción"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        return DescriptionPatternService.delete_pattern(db, user_id, pattern_id)
    
    @strawberry.mutation
    def apply_pattern_to_transactions(
        self,
        info: Info,
        pattern_id: int,
        transaction_ids: Optional[list[int]] = None
    ) -> int:
        """Aplicar un patrón específico a transacciones (retroactivamente)"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        # Obtener el patrón
        pattern = DescriptionPatternService.get_pattern_by_id(db, user_id, pattern_id)
        if not pattern:
            raise ValueError(f"Patrón {pattern_id} no encontrado")
        
        # Obtener transacciones objetivo
        from ...models.transactions import Transaction
        
        query = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.description.isnot(None)
        )
        
        if transaction_ids:
            query = query.filter(Transaction.id.in_(transaction_ids))
        
        transactions = query.all()
        
        applied_count = 0
        for transaction in transactions:
            desc = getattr(transaction, 'description', None)
            if desc and desc.strip():
                matched, matched_text = DescriptionPatternService.test_pattern_match(
                    pattern, str(desc)
                )
                
                if matched:
                    # Actualizar la transacción
                    old_subcategory_id = getattr(transaction, 'subcategory_id', None)
                    transaction.subcategory_id = pattern.subcategory_id
                    
                    # Registrar la coincidencia
                    from ...models.recurring_patterns import PatternMatch
                    from datetime import datetime
                    
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
        return applied_count
