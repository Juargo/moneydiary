import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class CategoryGroupType:
    id: int
    name: str
    is_expense: bool
    icon: Optional[str]
    display_order: int
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    # categories: List["CategoryType"] = strawberry.field(resolver=get_categories_in_group)

@strawberry.type
class CategoryType:
    id: int
    category_group_id: int
    name: str
    is_income: bool
    icon: Optional[str]
    display_order: int
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    # category_group: CategoryGroupType = strawberry.field(resolver=get_category_group)
    # subcategories: List["SubcategoryType"] = strawberry.field(resolver=get_subcategories)

@strawberry.type
class SubcategoryType:
    id: int
    category_id: int
    name: str
    display_order: int
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    # category: CategoryType = strawberry.field(resolver=get_category)