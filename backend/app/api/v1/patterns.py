from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from pydantic import BaseModel
from typing import Optional

from app.db.models.pattern import Pattern
from app.db.models.subcategory import Subcategory

router = APIRouter(prefix="/patterns", tags=["patterns"])

# Pydantic model for pattern creation
class PatternCreate(BaseModel):
    exp_name: str
    subcategory_id: int
    
@router.post("/", response_model=dict)
async def create_pattern(pattern: PatternCreate):
    """Create a new pattern for a subcategory"""
    try:
        # Verify subcategory exists
        subcategory = await Subcategory.get(id=pattern.subcategory_id)
        
        # Create pattern
        new_pattern = await Pattern.create(
            exp_name=pattern.exp_name,
            subcategory=subcategory
        )
        
        return {
            "id": new_pattern.id,
            "exp_name": new_pattern.exp_name,
            "subcategory_id": new_pattern.subcategory_id,
            "message": "Pattern created successfully"
        }
    except DoesNotExist:
        raise HTTPException(
            status_code=404, 
            detail=f"Subcategory with ID {pattern.subcategory_id} not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400, 
            detail=f"Pattern with expression '{pattern.exp_name}' already exists for this subcategory"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create pattern: {str(e)}"
        )

@router.delete("/{pattern_id}", response_model=dict)
async def delete_pattern(pattern_id: int):
    """Delete a pattern by its ID"""
    try:
        pattern = await Pattern.get(id=pattern_id)
        await pattern.delete()
        return {"message": f"Pattern with ID {pattern_id} deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Pattern with ID {pattern_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete pattern: {str(e)}")
