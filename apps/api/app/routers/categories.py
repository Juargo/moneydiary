from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..utils.fastapi_auth import get_current_user
from ..models.users import User
from ..schemas.categories import (
    CategoryGroupCreateRequest, CategoryGroupUpdateRequest, CategoryGroupResponse, CategoryGroupWithCategoriesResponse,
    CategoryCreateRequest, CategoryUpdateRequest, CategoryResponse, CategoryWithSubcategoriesResponse,
    SubcategoryCreateRequest, SubcategoryUpdateRequest, SubcategoryResponse
)
from ..services.category_service import (
    get_user_category_groups, get_category_group_by_id, create_category_group, update_category_group, delete_category_group,
    get_categories_by_group, get_category_by_id, create_category, update_category, delete_category,
    get_subcategories_by_category, get_subcategory_by_id, create_subcategory, update_subcategory, delete_subcategory
)

# Create router
router = APIRouter(prefix="/categories", tags=["categories"])


# Helper functions to convert models to responses
def subcategory_to_response(sub) -> SubcategoryResponse:
    """Convert Subcategory model to SubcategoryResponse"""
    return SubcategoryResponse(
        id=sub.id,  # type: ignore
        category_id=sub.category_id,  # type: ignore
        name=sub.name,  # type: ignore
        display_order=sub.display_order,  # type: ignore
        created_at=sub.created_at,  # type: ignore
        updated_at=sub.updated_at  # type: ignore
    )


def category_to_response_with_subcategories(category) -> CategoryWithSubcategoriesResponse:
    """Convert Category model to CategoryWithSubcategoriesResponse"""
    subcategories = [subcategory_to_response(sub) for sub in category.subcategories]
    
    return CategoryWithSubcategoriesResponse(
        id=category.id,  # type: ignore
        category_group_id=category.category_group_id,  # type: ignore
        name=category.name,  # type: ignore
        is_income=category.is_income,  # type: ignore
        icon=category.icon,  # type: ignore
        display_order=category.display_order,  # type: ignore
        created_at=category.created_at,  # type: ignore
        updated_at=category.updated_at,  # type: ignore
        subcategories=subcategories
    )


def category_group_to_response_with_categories(group) -> CategoryGroupWithCategoriesResponse:
    """Convert CategoryGroup model to CategoryGroupWithCategoriesResponse"""
    categories = [category_to_response_with_subcategories(cat) for cat in group.categories]
    
    return CategoryGroupWithCategoriesResponse(
        id=group.id,  # type: ignore
        name=group.name,  # type: ignore
        is_expense=group.is_expense,  # type: ignore
        icon=group.icon,  # type: ignore
        display_order=group.display_order,  # type: ignore
        created_at=group.created_at,  # type: ignore
        updated_at=group.updated_at,  # type: ignore
        categories=categories
    )


# CategoryGroup endpoints
@router.get("/groups", response_model=List[CategoryGroupWithCategoriesResponse])
async def get_category_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene todos los grupos de categorías del usuario autenticado"""
    try:
        user_id = current_user.id  # type: ignore
        groups = get_user_category_groups(db, user_id)
        return [category_group_to_response_with_categories(group) for group in groups]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving category groups: {str(e)}"
        )


@router.get("/groups/{group_id}", response_model=CategoryGroupWithCategoriesResponse)
async def get_category_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un grupo de categorías específico por ID"""
    user_id = current_user.id  # type: ignore
    group = get_category_group_by_id(db, user_id, group_id)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category group not found"
        )
    
    return category_group_to_response_with_categories(group)


@router.post("/groups", response_model=CategoryGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_category_group_endpoint(
    group_data: CategoryGroupCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea un nuevo grupo de categorías"""
    try:
        user_id = current_user.id  # type: ignore
        group = create_category_group(db, user_id, group_data)
        
        return CategoryGroupResponse(
            id=group.id,  # type: ignore
            name=group.name,  # type: ignore
            is_expense=group.is_expense,  # type: ignore
            icon=group.icon,  # type: ignore
            display_order=group.display_order,  # type: ignore
            created_at=group.created_at,  # type: ignore
            updated_at=group.updated_at  # type: ignore
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category group: {str(e)}"
        )


@router.put("/groups/{group_id}", response_model=CategoryGroupResponse)
async def update_category_group_endpoint(
    group_id: int,
    group_data: CategoryGroupUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un grupo de categorías existente"""
    user_id = current_user.id  # type: ignore
    group = update_category_group(db, user_id, group_id, group_data)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category group not found"
        )
    
    return CategoryGroupResponse(
        id=group.id,  # type: ignore
        name=group.name,  # type: ignore
        is_expense=group.is_expense,  # type: ignore
        icon=group.icon,  # type: ignore
        display_order=group.display_order,  # type: ignore
        created_at=group.created_at,  # type: ignore
        updated_at=group.updated_at  # type: ignore
    )


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_group_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un grupo de categorías"""
    user_id = current_user.id  # type: ignore
    success = delete_category_group(db, user_id, group_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category group not found"
        )


# Category endpoints
@router.get("/groups/{group_id}/categories", response_model=List[CategoryWithSubcategoriesResponse])
async def get_categories_by_group_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene todas las categorías de un grupo específico"""
    try:
        user_id = current_user.id  # type: ignore
        categories = get_categories_by_group(db, user_id, group_id)
        return [category_to_response_with_subcategories(cat) for cat in categories]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving categories: {str(e)}"
        )


@router.get("/{category_id}", response_model=CategoryWithSubcategoriesResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una categoría específica por ID"""
    user_id = current_user.id  # type: ignore
    category = get_category_by_id(db, user_id, category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category_to_response_with_subcategories(category)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category_endpoint(
    category_data: CategoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una nueva categoría"""
    try:
        user_id = current_user.id  # type: ignore
        category = create_category(db, user_id, category_data)
        
        return CategoryResponse(
            id=category.id,  # type: ignore
            category_group_id=category.category_group_id,  # type: ignore
            name=category.name,  # type: ignore
            is_income=category.is_income,  # type: ignore
            icon=category.icon,  # type: ignore
            display_order=category.display_order,  # type: ignore
            created_at=category.created_at,  # type: ignore
            updated_at=category.updated_at  # type: ignore
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category: {str(e)}"
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category_endpoint(
    category_id: int,
    category_data: CategoryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza una categoría existente"""
    user_id = current_user.id  # type: ignore
    category = update_category(db, user_id, category_id, category_data)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return CategoryResponse(
        id=category.id,  # type: ignore
        category_group_id=category.category_group_id,  # type: ignore
        name=category.name,  # type: ignore
        is_income=category.is_income,  # type: ignore
        icon=category.icon,  # type: ignore
        display_order=category.display_order,  # type: ignore
        created_at=category.created_at,  # type: ignore
        updated_at=category.updated_at  # type: ignore
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina una categoría"""
    user_id = current_user.id  # type: ignore
    success = delete_category(db, user_id, category_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )


# Subcategory endpoints
@router.get("/{category_id}/subcategories", response_model=List[SubcategoryResponse])
async def get_subcategories_by_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene todas las subcategorías de una categoría específica"""
    try:
        user_id = current_user.id  # type: ignore
        subcategories = get_subcategories_by_category(db, user_id, category_id)
        return [subcategory_to_response(sub) for sub in subcategories]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving subcategories: {str(e)}"
        )


@router.get("/subcategories/{subcategory_id}", response_model=SubcategoryResponse)
async def get_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una subcategoría específica por ID"""
    user_id = current_user.id  # type: ignore
    subcategory = get_subcategory_by_id(db, user_id, subcategory_id)
    
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found"
        )
    
    return subcategory_to_response(subcategory)


@router.post("/subcategories", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_subcategory_endpoint(
    subcategory_data: SubcategoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una nueva subcategoría"""
    try:
        user_id = current_user.id  # type: ignore
        subcategory = create_subcategory(db, user_id, subcategory_data)
        
        return subcategory_to_response(subcategory)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating subcategory: {str(e)}"
        )


@router.put("/subcategories/{subcategory_id}", response_model=SubcategoryResponse)
async def update_subcategory_endpoint(
    subcategory_id: int,
    subcategory_data: SubcategoryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza una subcategoría existente"""
    user_id = current_user.id  # type: ignore
    subcategory = update_subcategory(db, user_id, subcategory_id, subcategory_data)
    
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found"
        )
    
    return subcategory_to_response(subcategory)


@router.delete("/subcategories/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subcategory_endpoint(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina una subcategoría"""
    user_id = current_user.id  # type: ignore
    success = delete_subcategory(db, user_id, subcategory_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found"
        )
