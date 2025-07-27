import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum


@strawberry.enum
class PatternType(Enum):
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    EXACT = "exact"


@strawberry.type
class SubcategoryInfo:
    id: int
    name: str
    category_id: int = strawberry.field(name="categoryId")
    category_name: str = strawberry.field(name="categoryName")


@strawberry.type
class DescriptionPattern:
    id: int
    user_id: int = strawberry.field(name="userId")
    name: str
    pattern: str
    pattern_type: PatternType = strawberry.field(name="patternType")
    subcategory_id: int = strawberry.field(name="subcategoryId")
    subcategory: SubcategoryInfo
    priority: int
    is_case_sensitive: bool = strawberry.field(name="isCaseSensitive")
    is_active: bool = strawberry.field(name="isActive")
    auto_apply: bool = strawberry.field(name="autoApply")
    notes: Optional[str]
    created_at: Optional[datetime] = strawberry.field(name="createdAt")
    updated_at: Optional[datetime] = strawberry.field(name="updatedAt")


@strawberry.type
class PatternMatch:
    id: int
    transaction_id: int = strawberry.field(name="transactionId")
    pattern_id: int = strawberry.field(name="patternId")
    matched_text: Optional[str] = strawberry.field(name="matchedText")
    applied_at: Optional[datetime] = strawberry.field(name="appliedAt")
    was_manual_override: bool = strawberry.field(name="wasManualOverride")


@strawberry.type
class PatternTestResult:
    pattern_id: int = strawberry.field(name="patternId")
    pattern_name: str = strawberry.field(name="patternName")
    pattern: str
    pattern_type: PatternType = strawberry.field(name="patternType")
    matched: bool
    matched_text: Optional[str] = strawberry.field(name="matchedText")
    subcategory: SubcategoryInfo


@strawberry.type
class PatternTestResponse:
    description: str
    results: List[PatternTestResult]
    best_match: Optional[PatternTestResult] = strawberry.field(name="bestMatch")


@strawberry.type
class PatternSuggestion:
    suggested_pattern: str = strawberry.field(name="suggestedPattern")
    pattern_type: PatternType = strawberry.field(name="patternType")
    description_sample: str = strawberry.field(name="descriptionSample")
    occurrence_count: int = strawberry.field(name="occurrenceCount")
    suggested_subcategory_id: Optional[int] = strawberry.field(name="suggestedSubcategoryId")
    confidence_score: float = strawberry.field(name="confidenceScore")


@strawberry.type
class PatternSuggestionResponse:
    suggestions: List[PatternSuggestion]


@strawberry.type
class PatternStatistics:
    total_patterns: int = strawberry.field(name="totalPatterns")
    active_patterns: int = strawberry.field(name="activePatterns")
    auto_apply_patterns: int = strawberry.field(name="autoApplyPatterns")
    total_matches: int = strawberry.field(name="totalMatches")


# Input types for mutations
@strawberry.input
class DescriptionPatternCreateInput:
    name: str
    pattern: str
    pattern_type: PatternType = strawberry.field(name="patternType", default=PatternType.CONTAINS)
    subcategory_id: int = strawberry.field(name="subcategoryId")
    priority: int = 0
    is_case_sensitive: bool = strawberry.field(name="isCaseSensitive", default=False)
    is_active: bool = strawberry.field(name="isActive", default=True)
    auto_apply: bool = strawberry.field(name="autoApply", default=True)
    notes: Optional[str] = None


@strawberry.input
class DescriptionPatternUpdateInput:
    name: Optional[str] = None
    pattern: Optional[str] = None
    pattern_type: Optional[PatternType] = strawberry.field(name="patternType", default=None)
    subcategory_id: Optional[int] = strawberry.field(name="subcategoryId", default=None)
    priority: Optional[int] = None
    is_case_sensitive: Optional[bool] = strawberry.field(name="isCaseSensitive", default=None)
    is_active: Optional[bool] = strawberry.field(name="isActive", default=None)
    auto_apply: Optional[bool] = strawberry.field(name="autoApply", default=None)
    notes: Optional[str] = None


@strawberry.input
class PatternTestInput:
    description: str
    pattern_ids: Optional[List[int]] = strawberry.field(name="patternIds", default=None)


@strawberry.input
class PatternSuggestionInput:
    limit: int = 10
    min_occurrences: int = strawberry.field(name="minOccurrences", default=3)
