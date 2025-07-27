from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PatternType(str, Enum):
    """Tipos de patrones de descripción"""
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    EXACT = "exact"


class DescriptionPatternBase(BaseModel):
    """Base para patrones de descripción"""
    name: str = Field(..., description="Nombre descriptivo del patrón")
    pattern: str = Field(..., description="Patrón de texto a buscar")
    pattern_type: PatternType = Field(default=PatternType.CONTAINS, description="Tipo de patrón")
    subcategory_id: int = Field(..., description="ID de la subcategoría a asignar")
    priority: int = Field(default=0, description="Prioridad del patrón (mayor = se evalúa primero)")
    is_case_sensitive: bool = Field(default=False, description="Si el patrón es sensible a mayúsculas")
    is_active: bool = Field(default=True, description="Si el patrón está activo")
    auto_apply: bool = Field(default=True, description="Si se aplica automáticamente")
    notes: Optional[str] = Field(None, description="Notas adicionales")

    @validator('pattern')
    def pattern_not_empty(cls, v):
        if not v.strip():
            raise ValueError('El patrón no puede estar vacío')
        return v.strip()

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()


class DescriptionPatternCreate(DescriptionPatternBase):
    """Esquema para crear un patrón de descripción"""
    pass


class DescriptionPatternUpdate(BaseModel):
    """Esquema para actualizar un patrón de descripción"""
    name: Optional[str] = None
    pattern: Optional[str] = None
    pattern_type: Optional[PatternType] = None
    subcategory_id: Optional[int] = None
    priority: Optional[int] = None
    is_case_sensitive: Optional[bool] = None
    is_active: Optional[bool] = None
    auto_apply: Optional[bool] = None
    notes: Optional[str] = None

    @validator('pattern')
    def pattern_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El patrón no puede estar vacío')
        return v.strip() if v else v

    @validator('name')
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip() if v else v


class SubcategoryInfo(BaseModel):
    """Información básica de una subcategoría"""
    id: int
    name: str
    category_id: int
    category_name: str

    class Config:
        from_attributes = True


class DescriptionPatternResponse(DescriptionPatternBase):
    """Esquema de respuesta para un patrón de descripción"""
    id: int
    user_id: int
    subcategory: SubcategoryInfo
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatternMatchBase(BaseModel):
    """Base para coincidencias de patrones"""
    transaction_id: int
    pattern_id: int
    matched_text: Optional[str] = None
    was_manual_override: bool = False


class PatternMatchCreate(PatternMatchBase):
    """Esquema para crear una coincidencia de patrón"""
    pass


class PatternMatchResponse(PatternMatchBase):
    """Esquema de respuesta para una coincidencia de patrón"""
    id: int
    applied_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatternTestRequest(BaseModel):
    """Esquema para probar patrones contra una descripción"""
    description: str = Field(..., description="Descripción a probar")
    pattern_ids: Optional[List[int]] = Field(None, description="IDs específicos de patrones a probar")


class PatternTestResult(BaseModel):
    """Resultado de probar un patrón"""
    pattern_id: int
    pattern_name: str
    pattern: str
    pattern_type: PatternType
    matched: bool
    matched_text: Optional[str] = None
    subcategory: SubcategoryInfo


class PatternTestResponse(BaseModel):
    """Respuesta de prueba de patrones"""
    description: str
    results: List[PatternTestResult]
    best_match: Optional[PatternTestResult] = None  # El patrón con mayor prioridad que hizo match


class PatternSuggestionRequest(BaseModel):
    """Esquema para sugerir patrones basados en transacciones existentes"""
    limit: int = Field(default=10, description="Número máximo de sugerencias")
    min_occurrences: int = Field(default=3, description="Mínimo de ocurrencias para sugerir")


class PatternSuggestion(BaseModel):
    """Sugerencia de patrón"""
    suggested_pattern: str
    pattern_type: PatternType
    description_sample: str
    occurrence_count: int
    suggested_subcategory_id: Optional[int] = None
    confidence_score: float = Field(description="Puntuación de confianza (0-1)")


class PatternSuggestionResponse(BaseModel):
    """Respuesta de sugerencias de patrones"""
    suggestions: List[PatternSuggestion]
