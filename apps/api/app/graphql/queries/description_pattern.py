import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from strawberry.types import Info

from ..types.description_pattern import (
    DescriptionPattern,
    PatternTestResponse,
    PatternSuggestionResponse,
    PatternStatistics,
    PatternTestInput,
    PatternSuggestionInput,
    SubcategoryInfo,
    PatternType
)
from ...services.description_pattern_service import DescriptionPatternService
from ...schemas.description_patterns import (
    PatternTestRequest,
    PatternSuggestionRequest,
    PatternType as SchemaPatternType
)
from ...models.categories import Subcategory, Category


def convert_db_pattern_to_graphql(db_pattern) -> DescriptionPattern:
    """Convertir modelo de base de datos a tipo GraphQL"""
    return DescriptionPattern(
        id=db_pattern.id,
        user_id=db_pattern.user_id,
        name=db_pattern.name,
        pattern=db_pattern.pattern,
        pattern_type=PatternType(db_pattern.pattern_type),
        subcategory_id=db_pattern.subcategory_id,
        subcategory=convert_subcategory_to_info(db_pattern.subcategory),
        priority=db_pattern.priority,
        is_case_sensitive=db_pattern.is_case_sensitive,
        is_active=db_pattern.is_active,
        auto_apply=db_pattern.auto_apply,
        notes=db_pattern.notes,
        created_at=db_pattern.created_at,
        updated_at=db_pattern.updated_at
    )


def convert_subcategory_to_info(subcategory) -> SubcategoryInfo:
    """Convertir subcategoría a SubcategoryInfo"""
    return SubcategoryInfo(
        id=subcategory.id,
        name=subcategory.name,
        category_id=subcategory.category.id,
        category_name=subcategory.category.name
    )


def convert_pattern_type_to_graphql(pattern_type_str: str) -> PatternType:
    """Convertir string de pattern type a enum GraphQL"""
    type_mapping = {
        'contains': PatternType.CONTAINS,
        'starts_with': PatternType.STARTS_WITH,
        'ends_with': PatternType.ENDS_WITH,
        'regex': PatternType.REGEX,
        'exact': PatternType.EXACT
    }
    return type_mapping.get(pattern_type_str, PatternType.CONTAINS)


@strawberry.type
class DescriptionPatternQueries:
    
    @strawberry.field
    def my_description_patterns(
        self,
        info: Info,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[DescriptionPattern]:
        """Obtener los patrones de descripción del usuario actual"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        db_patterns = DescriptionPatternService.get_user_patterns(
            db, user_id, active_only, skip, limit
        )
        
        return [convert_db_pattern_to_graphql(pattern) for pattern in db_patterns]
    
    @strawberry.field
    def description_pattern(
        self,
        info: Info,
        pattern_id: int
    ) -> Optional[DescriptionPattern]:
        """Obtener un patrón específico por ID"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        db_pattern = DescriptionPatternService.get_pattern_by_id(db, user_id, pattern_id)
        
        if db_pattern:
            return convert_db_pattern_to_graphql(db_pattern)
        return None
    
    @strawberry.field
    def test_description_patterns(
        self,
        info: Info,
        input: PatternTestInput
    ) -> PatternTestResponse:
        """Probar patrones contra una descripción"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        request = PatternTestRequest(
            description=input.description,
            pattern_ids=input.pattern_ids
        )
        
        response = DescriptionPatternService.test_patterns(db, user_id, request)
        
        # Convertir a tipos GraphQL
        from ..types.description_pattern import PatternTestResult, PatternTestResponse, SubcategoryInfo
        
        graphql_results = []
        for result in response.results:
            graphql_result = PatternTestResult(
                pattern_id=result.pattern_id,
                pattern_name=result.pattern_name,
                pattern=result.pattern,
                pattern_type=convert_pattern_type_to_graphql(result.pattern_type.value),
                matched=result.matched,
                matched_text=result.matched_text,
                subcategory=SubcategoryInfo(
                    id=result.subcategory.id,
                    name=result.subcategory.name,
                    category_id=result.subcategory.category_id,
                    category_name=result.subcategory.category_name
                )
            )
            graphql_results.append(graphql_result)
        
        best_match = None
        if response.best_match:
            best_match = PatternTestResult(
                pattern_id=response.best_match.pattern_id,
                pattern_name=response.best_match.pattern_name,
                pattern=response.best_match.pattern,
                pattern_type=convert_pattern_type_to_graphql(response.best_match.pattern_type.value),
                matched=response.best_match.matched,
                matched_text=response.best_match.matched_text,
                subcategory=SubcategoryInfo(
                    id=response.best_match.subcategory.id,
                    name=response.best_match.subcategory.name,
                    category_id=response.best_match.subcategory.category_id,
                    category_name=response.best_match.subcategory.category_name
                )
            )
        
        return PatternTestResponse(
            description=response.description,
            results=graphql_results,
            best_match=best_match
        )
    
    @strawberry.field
    def suggest_description_patterns(
        self,
        info: Info,
        input: PatternSuggestionInput
    ) -> PatternSuggestionResponse:
        """Generar sugerencias de patrones basadas en transacciones existentes"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        request = PatternSuggestionRequest(
            limit=input.limit,
            min_occurrences=input.min_occurrences
        )
        
        response = DescriptionPatternService.generate_pattern_suggestions(db, user_id, request)
        
        # Convertir a tipos GraphQL
        from ..types.description_pattern import PatternSuggestion, PatternSuggestionResponse
        
        graphql_suggestions = []
        for suggestion in response.suggestions:
            graphql_suggestion = PatternSuggestion(
                suggested_pattern=suggestion.suggested_pattern,
                pattern_type=convert_pattern_type_to_graphql(suggestion.pattern_type.value),
                description_sample=suggestion.description_sample,
                occurrence_count=suggestion.occurrence_count,
                suggested_subcategory_id=suggestion.suggested_subcategory_id,
                confidence_score=suggestion.confidence_score
            )
            graphql_suggestions.append(graphql_suggestion)
        
        return PatternSuggestionResponse(suggestions=graphql_suggestions)
    
    @strawberry.field
    def description_pattern_statistics(self, info: Info) -> PatternStatistics:
        """Obtener estadísticas de patrones del usuario"""
        db: Session = info.context["db"]
        user_id = info.context["user_id"]
        
        stats = DescriptionPatternService.get_pattern_statistics(db, user_id)
        
        return PatternStatistics(
            total_patterns=stats['total_patterns'],
            active_patterns=stats['active_patterns'],
            auto_apply_patterns=stats['auto_apply_patterns'],
            total_matches=stats['total_matches']
        )
