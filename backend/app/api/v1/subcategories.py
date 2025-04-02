from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from pydantic import BaseModel
from typing import Optional

from app.db.models.subcategory import Subcategory
from app.db.models.category import Category

router = APIRouter(prefix="/subcategories", tags=["subcategories"])

# Pydantic model for subcategory creation
class SubcategoryCreate(BaseModel):
    name: str
    category_id: int
    
# Pydantic model for subcategory update
class SubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None

@router.post("/", response_model=dict)
async def create_subcategory(subcategory: SubcategoryCreate):
    """Create a new subcategory within a category"""
    try:
        # Verify category exists
        category = await Category.get(id=subcategory.category_id)
        
        # Create subcategory
        new_subcategory = await Subcategory.create(
            name=subcategory.name,
            category=category
        )
        
        return {
            "id": new_subcategory.id,
            "name": new_subcategory.name,
            "category_id": new_subcategory.category_id,
            "message": "Subcategory created successfully"
        }
    except DoesNotExist:
        raise HTTPException(
            status_code=404, 
            detail=f"Category with ID {subcategory.category_id} not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400, 
            detail=f"Subcategory with name '{subcategory.name}' already exists in this category"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create subcategory: {str(e)}"
        )

@router.patch("/{subcategory_id}", response_model=dict)
async def update_subcategory(subcategory_id: int, subcategory_data: SubcategoryUpdate):
    """Update a subcategory by its ID"""
    try:
        # Get the subcategory
        subcategory = await Subcategory.get(id=subcategory_id)
        
        # Update name if provided
        if subcategory_data.name is not None:
            subcategory.name = subcategory_data.name
        
        # Update category if provided
        if subcategory_data.category_id is not None:
            # Verify category exists
            category = await Category.get(id=subcategory_data.category_id)
            subcategory.category = category
        
        # Save the changes
        await subcategory.save()
        
        return {
            "id": subcategory.id,
            "name": subcategory.name,
            "category_id": subcategory.category_id,
            "message": "Subcategory updated successfully"
        }
    except DoesNotExist as e:
        if "Category" in str(e):
            raise HTTPException(
                status_code=404,
                detail=f"Category with ID {subcategory_data.category_id} not found"
            )
        raise HTTPException(
            status_code=404,
            detail=f"Subcategory with ID {subcategory_id} not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f"Subcategory with name '{subcategory_data.name}' already exists in this category"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update subcategory: {str(e)}"
        )

@router.delete("/{subcategory_id}", response_model=dict)
async def delete_subcategory(subcategory_id: int):
    """Delete a subcategory by its ID"""
    try:
        subcategory = await Subcategory.get(id=subcategory_id)
        await subcategory.delete()
        return {"message": f"Subcategory with ID {subcategory_id} deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Subcategory with ID {subcategory_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete subcategory: {str(e)}")
