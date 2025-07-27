"""
Utilidades para integrar patrones de descripción con transacciones
"""

from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..models.transactions import Transaction
from ..models.recurring_patterns import DescriptionPattern
from .description_pattern_service import DescriptionPatternService

logger = logging.getLogger(__name__)


def auto_categorize_transaction(db: Session, transaction: Transaction) -> Optional[DescriptionPattern]:
    """
    Categorizar automáticamente una transacción usando patrones de descripción.
    
    Esta función debe ser llamada después de crear o actualizar una transacción
    para aplicar automáticamente los patrones de descripción.
    
    Args:
        db: Sesión de base de datos
        transaction: Transacción a categorizar
    
    Returns:
        El patrón aplicado si se encontró una coincidencia, None en caso contrario
    """
    try:
        return DescriptionPatternService.apply_patterns_to_transaction(db, transaction)
    except Exception as e:
        logger.error(f"Error auto-categorizando transacción {transaction.id}: {str(e)}")
        return None


def suggest_patterns_for_user(db: Session, user_id: int, min_occurrences: int = 3) -> dict:
    """
    Generar sugerencias de patrones para un usuario basadas en sus transacciones.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        min_occurrences: Número mínimo de ocurrencias para sugerir un patrón
    
    Returns:
        Diccionario con sugerencias de patrones
    """
    try:
        from ..schemas.description_patterns import PatternSuggestionRequest
        
        request = PatternSuggestionRequest(
            limit=20,
            min_occurrences=min_occurrences
        )
        
        response = DescriptionPatternService.generate_pattern_suggestions(db, user_id, request)
        
        return {
            'success': True,
            'suggestions': [
                {
                    'pattern': s.suggested_pattern,
                    'type': s.pattern_type.value,
                    'sample': s.description_sample,
                    'count': s.occurrence_count,
                    'confidence': s.confidence_score,
                    'subcategory_id': s.suggested_subcategory_id
                }
                for s in response.suggestions
            ]
        }
    except Exception as e:
        logger.error(f"Error generando sugerencias para usuario {user_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'suggestions': []
        }


def apply_patterns_bulk(db: Session, user_id: int, pattern_ids: Optional[list] = None) -> dict:
    """
    Aplicar patrones en lote a todas las transacciones de un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        pattern_ids: Lista de IDs de patrones específicos (opcional)
    
    Returns:
        Diccionario con el resultado de la operación
    """
    try:
        from ..models.transactions import Transaction
        
        # Obtener transacciones del usuario
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.description.isnot(None)
        ).all()
        
        # Obtener patrones del usuario
        patterns = DescriptionPatternService.get_user_patterns(
            db, user_id, active_only=True
        )
        
        if pattern_ids:
            patterns = [p for p in patterns if p.id in pattern_ids]
        
        applied_count = 0
        total_transactions = len(transactions)
        
        for transaction in transactions:
            desc = getattr(transaction, 'description', None)
            if desc and str(desc).strip():
                # Encontrar el patrón con mayor prioridad que coincida
                for pattern in sorted(patterns, key=lambda x: getattr(x, 'priority', 0), reverse=True):
                    matched, matched_text = DescriptionPatternService.test_pattern_match(
                        pattern, str(desc)
                    )
                    
                    if matched:
                        # Solo aplicar si la transacción no tiene subcategoría o si es diferente
                        current_subcategory = getattr(transaction, 'subcategory_id', None)
                        if current_subcategory != pattern.subcategory_id:
                            transaction.subcategory_id = pattern.subcategory_id
                            applied_count += 1
                        break  # Solo aplicar el primer patrón que coincida
        
        db.commit()
        
        return {
            'success': True,
            'total_transactions': total_transactions,
            'applied_count': applied_count,
            'percentage': (applied_count / total_transactions * 100) if total_transactions > 0 else 0
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error aplicando patrones en lote para usuario {user_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'total_transactions': 0,
            'applied_count': 0,
            'percentage': 0
        }


def validate_pattern_regex(pattern: str) -> dict:
    """
    Validar que un patrón regex sea válido.
    
    Args:
        pattern: Patrón regex a validar
    
    Returns:
        Diccionario con el resultado de la validación
    """
    try:
        import re
        re.compile(pattern)
        return {
            'valid': True,
            'message': 'Patrón regex válido'
        }
    except re.error as e:
        return {
            'valid': False,
            'message': f'Patrón regex inválido: {str(e)}'
        }


def get_pattern_performance_stats(db: Session, user_id: int) -> dict:
    """
    Obtener estadísticas de rendimiento de los patrones del usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
    
    Returns:
        Diccionario con estadísticas de rendimiento
    """
    try:
        from ..models.recurring_patterns import PatternMatch
        from sqlalchemy import func, desc
        
        # Obtener estadísticas de coincidencias por patrón
        pattern_stats = db.query(
            DescriptionPattern.id,
            DescriptionPattern.name,
            DescriptionPattern.pattern,
            func.count(PatternMatch.id).label('match_count')
        ).join(
            PatternMatch, DescriptionPattern.id == PatternMatch.pattern_id, isouter=True
        ).filter(
            DescriptionPattern.user_id == user_id
        ).group_by(
            DescriptionPattern.id, DescriptionPattern.name, DescriptionPattern.pattern
        ).order_by(desc('match_count')).all()
        
        # Obtener total de transacciones sin categorizar
        from ..models.transactions import Transaction
        
        uncategorized_count = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.subcategory_id.is_(None),
            Transaction.description.isnot(None)
        ).count()
        
        total_transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).count()
        
        return {
            'success': True,
            'pattern_performance': [
                {
                    'pattern_id': stat.id,
                    'pattern_name': stat.name,
                    'pattern': stat.pattern,
                    'match_count': stat.match_count
                }
                for stat in pattern_stats
            ],
            'uncategorized_transactions': uncategorized_count,
            'total_transactions': total_transactions,
            'categorization_rate': ((total_transactions - uncategorized_count) / total_transactions * 100) 
                                 if total_transactions > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de rendimiento para usuario {user_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'pattern_performance': [],
            'uncategorized_transactions': 0,
            'total_transactions': 0,
            'categorization_rate': 0
        }
