from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from pydantic import BaseModel
from typing import Optional

from app.db.models.pattern import Pattern
from app.db.models.subcategory import Subcategory

router = APIRouter(prefix="/patterns", tags=["patterns"])

# Pydantic model for pattern creation
class PatternCreate(BaseModel):
    match_text: str
    subcategory_id: int

# Pydantic model for pattern update - only update match_text now
class PatternUpdate(BaseModel):
    match_text: Optional[str] = None
    
@router.post("/", response_model=dict)
async def create_pattern(pattern: PatternCreate):
    """Create a new pattern for a subcategory"""
    try:
        # Verify subcategory exists
        subcategory = await Subcategory.get(id=pattern.subcategory_id)
        
        # Create pattern
        new_pattern = await Pattern.create(
            match_text=pattern.match_text,
            subcategory=subcategory
        )
        
        return {
            "id": new_pattern.id,
            "match_text": new_pattern.match_text,
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
            detail=f"Pattern with expression '{pattern.match_text}' already exists for this subcategory"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create pattern: {str(e)}"
        )

@router.patch("/{pattern_id}", response_model=dict)
async def update_pattern(pattern_id: int, pattern_data: PatternUpdate):
    """Update a pattern by its ID"""
    try:
        # Get the pattern
        pattern = await Pattern.get(id=pattern_id)
        
        # Update match_text if provided
        if pattern_data.match_text is not None:
            pattern.match_text = pattern_data.match_text
        
        # Save the changes
        await pattern.save()
        
        return {
            "id": pattern.id,
            "match_text": pattern.match_text,
            "subcategory_id": pattern.subcategory_id,
            "message": "Pattern updated successfully"
        }
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail=f"Pattern with ID {pattern_id} not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f"Pattern with expression '{pattern_data.match_text}' already exists for this subcategory"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update pattern: {str(e)}"
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
