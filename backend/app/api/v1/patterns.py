from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist

from app.db.models.pattern import Pattern

router = APIRouter(prefix="/patterns", tags=["patterns"])

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
