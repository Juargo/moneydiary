from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# CategoryGroup schemas
class CategoryGroupCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del grupo de categorías")
    is_expense: bool = Field(..., description="Si es grupo de gastos (True) o ingresos (False)")
    icon: Optional[str] = Field(None, max_length=50, description="Icono del grupo")
    display_order: Optional[int] = Field(0, description="Orden de visualización")


class CategoryGroupUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del grupo de categorías")
    is_expense: Optional[bool] = Field(None, description="Si es grupo de gastos (True) o ingresos (False)")
    icon: Optional[str] = Field(None, max_length=50, description="Icono del grupo")
    display_order: Optional[int] = Field(None, description="Orden de visualización")


class CategoryGroupResponse(BaseModel):
    id: int
    name: str
    is_expense: bool
    icon: Optional[str] = None
    display_order: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Category schemas
class CategoryCreateRequest(BaseModel):
    category_group_id: int = Field(..., gt=0, description="ID del grupo de categorías")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la categoría")
    is_income: bool = Field(..., description="Si es categoría de ingresos")
    icon: Optional[str] = Field(None, max_length=50, description="Icono de la categoría")
    display_order: Optional[int] = Field(0, description="Orden de visualización")


class CategoryUpdateRequest(BaseModel):
    category_group_id: Optional[int] = Field(None, gt=0, description="ID del grupo de categorías")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la categoría")
    is_income: Optional[bool] = Field(None, description="Si es categoría de ingresos")
    icon: Optional[str] = Field(None, max_length=50, description="Icono de la categoría")
    display_order: Optional[int] = Field(None, description="Orden de visualización")


class CategoryResponse(BaseModel):
    id: int
    category_group_id: int
    name: str
    is_income: bool
    icon: Optional[str] = None
    display_order: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Subcategory schemas
class SubcategoryCreateRequest(BaseModel):
    category_id: int = Field(..., gt=0, description="ID de la categoría")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la subcategoría")
    display_order: Optional[int] = Field(0, description="Orden de visualización")


class SubcategoryUpdateRequest(BaseModel):
    category_id: Optional[int] = Field(None, gt=0, description="ID de la categoría")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la subcategoría")
    display_order: Optional[int] = Field(None, description="Orden de visualización")


class SubcategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str
    display_order: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Complete responses with relationships
class CategoryWithSubcategoriesResponse(CategoryResponse):
    subcategories: List[SubcategoryResponse] = []


class CategoryGroupWithCategoriesResponse(CategoryGroupResponse):
    categories: List[CategoryWithSubcategoriesResponse] = []
