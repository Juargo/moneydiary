from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import re
import logging
from collections import Counter

from ..models.recurring_patterns import DescriptionPattern, PatternMatch
from ..models.transactions import Transaction
from ..models.categories import Subcategory, Category
from ..schemas.description_patterns import (
    DescriptionPatternCreate, 
    DescriptionPatternUpdate,
    PatternTestRequest,
    PatternTestResult,
    PatternTestResponse,
    PatternSuggestionRequest,
    PatternSuggestion,
    PatternSuggestionResponse,
    PatternType,
    SubcategoryInfo
)

logger = logging.getLogger(__name__)


class DescriptionPatternService:
    """Servicio para manejar patrones de descripción de transacciones"""

    @staticmethod
    def create_pattern(db: Session, user_id: int, pattern_data: DescriptionPatternCreate) -> DescriptionPattern:
        """Crear un nuevo patrón de descripción"""
        try:
            # Verificar que la subcategoría existe y pertenece a una categoría válida
            subcategory = db.query(Subcategory).filter(
                Subcategory.id == pattern_data.subcategory_id
            ).first()
            
            if not subcategory:
                raise ValueError(f"Subcategoría con ID {pattern_data.subcategory_id} no encontrada")

            # Validar patrón regex si es necesario
            if pattern_data.pattern_type == PatternType.REGEX:
                try:
                    re.compile(pattern_data.pattern)
                except re.error as e:
                    raise ValueError(f"Patrón regex inválido: {str(e)}")

            db_pattern = DescriptionPattern(
                user_id=user_id,
                name=pattern_data.name,
                pattern=pattern_data.pattern,
                pattern_type=pattern_data.pattern_type.value,
                subcategory_id=pattern_data.subcategory_id,
                priority=pattern_data.priority,
                is_case_sensitive=pattern_data.is_case_sensitive,
                is_active=pattern_data.is_active,
                auto_apply=pattern_data.auto_apply,
                notes=pattern_data.notes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(db_pattern)
            db.commit()
            db.refresh(db_pattern)
            
            logger.info(f"Patrón de descripción creado: {db_pattern.id} para usuario {user_id}")
            return db_pattern

        except Exception as e:
            db.rollback()
            logger.error(f"Error creando patrón de descripción: {str(e)}")
            raise

    @staticmethod
    def get_user_patterns(
        db: Session, 
        user_id: int, 
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[DescriptionPattern]:
        """Obtener patrones de un usuario"""
        query = db.query(DescriptionPattern).options(
            joinedload(DescriptionPattern.subcategory).joinedload(Subcategory.category)
        ).filter(DescriptionPattern.user_id == user_id)
        
        if active_only:
            query = query.filter(DescriptionPattern.is_active == True)
        
        query = query.order_by(desc(DescriptionPattern.priority), asc(DescriptionPattern.name))
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_pattern_by_id(db: Session, user_id: int, pattern_id: int) -> Optional[DescriptionPattern]:
        """Obtener un patrón específico por ID"""
        return db.query(DescriptionPattern).options(
            joinedload(DescriptionPattern.subcategory).joinedload(Subcategory.category)
        ).filter(
            and_(
                DescriptionPattern.id == pattern_id,
                DescriptionPattern.user_id == user_id
            )
        ).first()

    @staticmethod
    def update_pattern(
        db: Session, 
        user_id: int, 
        pattern_id: int, 
        pattern_data: DescriptionPatternUpdate
    ) -> Optional[DescriptionPattern]:
        """Actualizar un patrón existente"""
        try:
            db_pattern = DescriptionPatternService.get_pattern_by_id(db, user_id, pattern_id)
            if not db_pattern:
                return None

            # Actualizar solo los campos proporcionados
            update_data = pattern_data.dict(exclude_unset=True)
            
            # Validaciones específicas
            if 'subcategory_id' in update_data:
                subcategory = db.query(Subcategory).filter(
                    Subcategory.id == update_data['subcategory_id']
                ).first()
                if not subcategory:
                    raise ValueError(f"Subcategoría con ID {update_data['subcategory_id']} no encontrada")

            if 'pattern' in update_data and 'pattern_type' in update_data:
                if update_data['pattern_type'] == PatternType.REGEX.value:
                    try:
                        re.compile(update_data['pattern'])
                    except re.error as e:
                        raise ValueError(f"Patrón regex inválido: {str(e)}")

            # Aplicar actualizaciones
            for field, value in update_data.items():
                if hasattr(db_pattern, field):
                    setattr(db_pattern, field, value)
            
            db_pattern.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_pattern)
            
            logger.info(f"Patrón de descripción actualizado: {pattern_id}")
            return db_pattern

        except Exception as e:
            db.rollback()
            logger.error(f"Error actualizando patrón de descripción: {str(e)}")
            raise

    @staticmethod
    def delete_pattern(db: Session, user_id: int, pattern_id: int) -> bool:
        """Eliminar un patrón"""
        try:
            db_pattern = DescriptionPatternService.get_pattern_by_id(db, user_id, pattern_id)
            if not db_pattern:
                return False

            # Eliminar registros de coincidencias relacionados
            db.query(PatternMatch).filter(PatternMatch.pattern_id == pattern_id).delete()
            
            # Eliminar el patrón
            db.delete(db_pattern)
            db.commit()
            
            logger.info(f"Patrón de descripción eliminado: {pattern_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error eliminando patrón de descripción: {str(e)}")
            raise

    @staticmethod
    def test_pattern_match(pattern: DescriptionPattern, description: str) -> Tuple[bool, Optional[str]]:
        """Probar si un patrón coincide con una descripción"""
        if not description:
            return False, None

        text_to_test = description if pattern.is_case_sensitive else description.lower()
        pattern_text = pattern.pattern if pattern.is_case_sensitive else pattern.pattern.lower()

        try:
            if pattern.pattern_type == PatternType.EXACT.value:
                matched = text_to_test == pattern_text
                return matched, description if matched else None
                
            elif pattern.pattern_type == PatternType.CONTAINS.value:
                matched = pattern_text in text_to_test
                return matched, pattern.pattern if matched else None
                
            elif pattern.pattern_type == PatternType.STARTS_WITH.value:
                matched = text_to_test.startswith(pattern_text)
                return matched, pattern.pattern if matched else None
                
            elif pattern.pattern_type == PatternType.ENDS_WITH.value:
                matched = text_to_test.endswith(pattern_text)
                return matched, pattern.pattern if matched else None
                
            elif pattern.pattern_type == PatternType.REGEX.value:
                flags = 0 if pattern.is_case_sensitive else re.IGNORECASE
                match = re.search(pattern.pattern, description, flags)
                if match:
                    return True, match.group(0)
                return False, None
                
        except Exception as e:
            logger.warning(f"Error probando patrón {pattern.id}: {str(e)}")
            return False, None

        return False, None

    @staticmethod
    def test_patterns(db: Session, user_id: int, request: PatternTestRequest) -> PatternTestResponse:
        """Probar patrones contra una descripción"""
        patterns_query = db.query(DescriptionPattern).options(
            joinedload(DescriptionPattern.subcategory).joinedload(Subcategory.category)
        ).filter(
            and_(
                DescriptionPattern.user_id == user_id,
                DescriptionPattern.is_active == True
            )
        )

        if request.pattern_ids:
            patterns_query = patterns_query.filter(
                DescriptionPattern.id.in_(request.pattern_ids)
            )

        patterns = patterns_query.order_by(desc(DescriptionPattern.priority)).all()

        results = []
        best_match = None

        for pattern in patterns:
            matched, matched_text = DescriptionPatternService.test_pattern_match(
                pattern, request.description
            )

            result = PatternTestResult(
                pattern_id=pattern.id,
                pattern_name=pattern.name,
                pattern=pattern.pattern,
                pattern_type=PatternType(pattern.pattern_type),
                matched=matched,
                matched_text=matched_text,
                subcategory=SubcategoryInfo(
                    id=pattern.subcategory.id,
                    name=pattern.subcategory.name,
                    category_id=pattern.subcategory.category.id,
                    category_name=pattern.subcategory.category.name
                )
            )

            results.append(result)

            # El primer match (mayor prioridad) es el mejor
            if matched and best_match is None:
                best_match = result

        return PatternTestResponse(
            description=request.description,
            results=results,
            best_match=best_match
        )

    @staticmethod
    def find_matching_patterns(db: Session, user_id: int, description: str) -> List[DescriptionPattern]:
        """Encontrar patrones que coincidan con una descripción"""
        patterns = db.query(DescriptionPattern).filter(
            and_(
                DescriptionPattern.user_id == user_id,
                DescriptionPattern.is_active == True
            )
        ).order_by(desc(DescriptionPattern.priority)).all()

        matching_patterns = []
        for pattern in patterns:
            matched, _ = DescriptionPatternService.test_pattern_match(pattern, description)
            if matched:
                matching_patterns.append(pattern)

        return matching_patterns

    @staticmethod
    def apply_patterns_to_transaction(db: Session, transaction: Transaction) -> Optional[DescriptionPattern]:
        """Aplicar patrones automáticamente a una transacción"""
        description = getattr(transaction, 'description', None)
        if not description or not str(description).strip():
            return None

        user_id = getattr(transaction, 'user_id', None)
        if not user_id:
            return None

        matching_patterns = DescriptionPatternService.find_matching_patterns(
            db, int(user_id), str(description)
        )

        # Aplicar el primer patrón que coincida (mayor prioridad) y tenga auto_apply=True
        for pattern in matching_patterns:
            auto_apply = getattr(pattern, 'auto_apply', False)
            if auto_apply:
                # Actualizar la transacción
                transaction.subcategory_id = pattern.subcategory_id
                
                # Registrar la coincidencia
                match_record = PatternMatch(
                    transaction_id=transaction.id,
                    pattern_id=pattern.id,
                    matched_text=pattern.pattern,
                    applied_at=datetime.utcnow(),
                    was_manual_override=False
                )
                db.add(match_record)
                
                logger.info(f"Patrón {pattern.id} aplicado automáticamente a transacción {transaction.id}")
                return pattern

        return None

    @staticmethod
    def generate_pattern_suggestions(
        db: Session, 
        user_id: int, 
        request: PatternSuggestionRequest
    ) -> PatternSuggestionResponse:
        """Generar sugerencias de patrones basadas en transacciones existentes"""
        # Obtener transacciones del usuario con subcategorías asignadas
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.description.isnot(None),
                Transaction.subcategory_id.isnot(None)
            )
        ).all()

        # Agrupar por subcategoría y analizar descripciones
        subcategory_descriptions = {}
        for transaction in transactions:
            if transaction.subcategory_id not in subcategory_descriptions:
                subcategory_descriptions[transaction.subcategory_id] = []
            subcategory_descriptions[transaction.subcategory_id].append(transaction.description.strip())

        suggestions = []

        for subcategory_id, descriptions in subcategory_descriptions.items():
            if len(descriptions) < request.min_occurrences:
                continue

            # Analizar patrones comunes
            suggested_patterns = DescriptionPatternService._analyze_descriptions(descriptions)
            
            for pattern_info in suggested_patterns:
                if pattern_info['count'] >= request.min_occurrences:
                    confidence = min(pattern_info['count'] / len(descriptions), 1.0)
                    
                    suggestion = PatternSuggestion(
                        suggested_pattern=pattern_info['pattern'],
                        pattern_type=pattern_info['type'],
                        description_sample=pattern_info['sample'],
                        occurrence_count=pattern_info['count'],
                        suggested_subcategory_id=subcategory_id,
                        confidence_score=confidence
                    )
                    suggestions.append(suggestion)

        # Ordenar por puntuación de confianza y número de ocurrencias
        suggestions.sort(key=lambda x: (x.confidence_score, x.occurrence_count), reverse=True)
        
        return PatternSuggestionResponse(
            suggestions=suggestions[:request.limit]
        )

    @staticmethod
    def _analyze_descriptions(descriptions: List[str]) -> List[Dict[str, Any]]:
        """Analizar descripciones para encontrar patrones comunes"""
        patterns = []
        
        # Análisis de palabras comunes
        all_words = []
        for desc in descriptions:
            words = desc.lower().split()
            all_words.extend(words)
        
        word_counts = Counter(all_words)
        
        # Sugerir patrones basados en palabras frecuentes
        for word, count in word_counts.most_common(10):
            if len(word) > 2 and count >= 2:  # Filtrar palabras muy cortas o poco frecuentes
                matching_descriptions = [desc for desc in descriptions if word.lower() in desc.lower()]
                if matching_descriptions:
                    patterns.append({
                        'pattern': word,
                        'type': PatternType.CONTAINS,
                        'count': len(matching_descriptions),
                        'sample': matching_descriptions[0]
                    })

        # Análisis de prefijos comunes
        if len(descriptions) > 1:
            # Encontrar prefijos comunes de 4+ caracteres
            for length in range(4, min(20, max(len(d) for d in descriptions) + 1)):
                prefix_counts = Counter()
                for desc in descriptions:
                    if len(desc) >= length:
                        prefix = desc[:length].strip()
                        if prefix:
                            prefix_counts[prefix] += 1
                
                for prefix, count in prefix_counts.items():
                    if count >= 2:
                        matching_descriptions = [desc for desc in descriptions if desc.startswith(prefix)]
                        patterns.append({
                            'pattern': prefix,
                            'type': PatternType.STARTS_WITH,
                            'count': count,
                            'sample': matching_descriptions[0]
                        })

        return patterns

    @staticmethod
    def get_pattern_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """Obtener estadísticas de patrones del usuario"""
        total_patterns = db.query(DescriptionPattern).filter(
            DescriptionPattern.user_id == user_id
        ).count()

        active_patterns = db.query(DescriptionPattern).filter(
            and_(
                DescriptionPattern.user_id == user_id,
                DescriptionPattern.is_active == True
            )
        ).count()

        auto_apply_patterns = db.query(DescriptionPattern).filter(
            and_(
                DescriptionPattern.user_id == user_id,
                DescriptionPattern.is_active == True,
                DescriptionPattern.auto_apply == True
            )
        ).count()

        total_matches = db.query(PatternMatch).join(DescriptionPattern).filter(
            DescriptionPattern.user_id == user_id
        ).count()

        return {
            'total_patterns': total_patterns,
            'active_patterns': active_patterns,
            'auto_apply_patterns': auto_apply_patterns,
            'total_matches': total_matches
        }
