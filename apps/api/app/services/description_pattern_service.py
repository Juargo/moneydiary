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
        # Obtener TODAS las transacciones del usuario con descripción (categorizadas y no categorizadas)
        all_transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.description.isnot(None),
                Transaction.description != ""
            )
        ).all()

        if not all_transactions:
            return PatternSuggestionResponse(suggestions=[])

        # Separar transacciones categorizadas y no categorizadas
        categorized_transactions = [t for t in all_transactions if t.subcategory_id is not None]
        uncategorized_transactions = [t for t in all_transactions if t.subcategory_id is None]
        
        suggestions = []

        # 1. Analizar transacciones ya categorizadas (algoritmo original)
        if categorized_transactions:
            suggestions.extend(
                DescriptionPatternService._analyze_categorized_transactions(
                    categorized_transactions, request
                )
            )

        # 2. Analizar transacciones NO categorizadas para encontrar patrones repetidos
        if uncategorized_transactions:
            suggestions.extend(
                DescriptionPatternService._analyze_uncategorized_transactions(
                    uncategorized_transactions, request
                )
            )

        # Eliminar duplicados y ordenar por puntuación de confianza y número de ocurrencias
        unique_suggestions = {}
        for suggestion in suggestions:
            key = f"{suggestion.suggested_pattern}_{suggestion.pattern_type}"
            if key not in unique_suggestions or suggestion.confidence_score > unique_suggestions[key].confidence_score:
                unique_suggestions[key] = suggestion

        final_suggestions = list(unique_suggestions.values())
        final_suggestions.sort(key=lambda x: (x.confidence_score, x.occurrence_count), reverse=True)
        
        return PatternSuggestionResponse(
            suggestions=final_suggestions[:request.limit]
        )

    @staticmethod
    def _analyze_categorized_transactions(transactions: List[Transaction], request: PatternSuggestionRequest) -> List[PatternSuggestion]:
        """Analizar transacciones categorizadas para generar sugerencias"""
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

        return suggestions

    @staticmethod
    def _analyze_uncategorized_transactions(transactions: List[Transaction], request: PatternSuggestionRequest) -> List[PatternSuggestion]:
        """Analizar transacciones NO categorizadas para encontrar patrones repetidos"""
        descriptions = [t.description.strip() for t in transactions]
        
        if len(descriptions) < request.min_occurrences:
            return []

        suggestions = []
        
        # Analizar patrones comunes en descripciones no categorizadas
        suggested_patterns = DescriptionPatternService._analyze_descriptions(descriptions)
        
        for pattern_info in suggested_patterns:
            if pattern_info['count'] >= request.min_occurrences:
                # Para transacciones no categorizadas, la confianza se basa en la frecuencia
                confidence = min(pattern_info['count'] / len(descriptions), 0.8)  # Máximo 0.8 para no categorizadas
                
                suggestion = PatternSuggestion(
                    suggested_pattern=pattern_info['pattern'],
                    pattern_type=pattern_info['type'],
                    description_sample=pattern_info['sample'],
                    occurrence_count=pattern_info['count'],
                    suggested_subcategory_id=None,  # Sin subcategoría sugerida
                    confidence_score=confidence
                )
                suggestions.append(suggestion)

        return suggestions

    @staticmethod
    def _analyze_descriptions(descriptions: List[str]) -> List[Dict[str, Any]]:
        """Analizar descripciones para encontrar patrones comunes mejorado"""
        patterns = []
        
        # Filtrar descripciones vacías o muy cortas
        valid_descriptions = [desc for desc in descriptions if len(desc.strip()) >= 3]
        if len(valid_descriptions) < 2:
            return patterns
        
        # 1. Análisis de palabras comunes (mejorado)
        all_words = []
        for desc in valid_descriptions:
            # Limpiar y normalizar palabras
            words = desc.lower().replace(',', ' ').replace('.', ' ').split()
            # Filtrar palabras comunes en español que no son útiles
            stop_words = {'de', 'la', 'el', 'en', 'a', 'y', 'que', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'una', 'sus', 'les', 'del', 'las', 'al', 'un', 'ser', 'son', 'está', 'están'}
            filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
            all_words.extend(filtered_words)
        
        word_counts = Counter(all_words)
        
        # Sugerir patrones basados en palabras frecuentes
        for word, count in word_counts.most_common(15):
            if count >= 2:  # Al menos 2 ocurrencias
                matching_descriptions = [desc for desc in valid_descriptions if word.lower() in desc.lower()]
                if len(matching_descriptions) >= 2:
                    patterns.append({
                        'pattern': word,
                        'type': PatternType.CONTAINS,
                        'count': len(matching_descriptions),
                        'sample': matching_descriptions[0]
                    })

        # 2. Análisis de prefijos comunes (mejorado)
        if len(valid_descriptions) > 1:
            # Encontrar prefijos comunes de diferentes longitudes
            for length in range(4, min(25, max(len(d) for d in valid_descriptions) + 1)):
                prefix_counts = Counter()
                for desc in valid_descriptions:
                    if len(desc) >= length:
                        prefix = desc[:length].strip()
                        # Solo considerar prefijos que no terminen en medio de una palabra
                        if prefix and (len(desc) == length or desc[length] == ' '):
                            prefix_counts[prefix] += 1
                
                for prefix, count in prefix_counts.items():
                    if count >= 2 and len(prefix.strip()) > 3:
                        matching_descriptions = [desc for desc in valid_descriptions if desc.startswith(prefix)]
                        patterns.append({
                            'pattern': prefix.strip(),
                            'type': PatternType.STARTS_WITH,
                            'count': count,
                            'sample': matching_descriptions[0]
                        })

        # 3. Análisis de sufijos comunes
        if len(valid_descriptions) > 1:
            for length in range(4, min(20, max(len(d) for d in valid_descriptions) + 1)):
                suffix_counts = Counter()
                for desc in valid_descriptions:
                    if len(desc) >= length:
                        suffix = desc[-length:].strip()
                        # Solo considerar sufijos que no empiecen en medio de una palabra
                        if suffix and (length == len(desc) or desc[-(length+1)] == ' '):
                            suffix_counts[suffix] += 1
                
                for suffix, count in suffix_counts.items():
                    if count >= 2 and len(suffix.strip()) > 3:
                        matching_descriptions = [desc for desc in valid_descriptions if desc.endswith(suffix)]
                        patterns.append({
                            'pattern': suffix.strip(),
                            'type': PatternType.ENDS_WITH,
                            'count': count,
                            'sample': matching_descriptions[0]
                        })

        # 4. Análisis de descripciones exactas repetidas
        exact_counts = Counter(valid_descriptions)
        for description, count in exact_counts.items():
            if count >= 2:
                patterns.append({
                    'pattern': description,
                    'type': PatternType.EXACT,
                    'count': count,
                    'sample': description
                })

        # Eliminar patrones duplicados y muy similares
        unique_patterns = []
        seen_patterns = set()
        
        for pattern in patterns:
            pattern_key = f"{pattern['pattern'].lower()}_{pattern['type']}"
            if pattern_key not in seen_patterns:
                seen_patterns.add(pattern_key)
                unique_patterns.append(pattern)

        return unique_patterns

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
