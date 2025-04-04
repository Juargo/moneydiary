"""
API endpoints for managing Pattern Ignore records
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime
from app.db.models.pattern_ignore import PatternIgnore
from app.db.models.user import User


router = APIRouter(
    prefix="/pattern-ignores",
    tags=["pattern-ignores"]
)


class PatternIgnoreCreate(BaseModel):
    """Schema for creating a pattern ignore"""
    exp_name: str
    description: str


class PatternIgnoreUpdate(BaseModel):
    """Schema for updating a pattern ignore"""
    exp_name: Optional[str] = None
    description: Optional[str] = None


class PatternIgnoreResponse(BaseModel):
    """Schema for pattern ignore response"""
    id: int
    exp_name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config"""
        orm_mode = True
        # Ensure JSON serialization works correctly for datetime fields
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


async def get_default_user():
    """Get the default user with ID 1"""
    try:
        user = await User.get(id=1)
        return user
    except Exception as e:
        # Handle the case where the user doesn't exist
        # In a real application, you might want to log this error
        print(f"Error fetching default user: {e}")
        # Create a mock user for development purposes
        # This is not recommended for production
        return User(id=1)


@router.post("/", response_model=PatternIgnoreResponse, status_code=status.HTTP_201_CREATED)
async def create_pattern_ignore(
    pattern_ignore: PatternIgnoreCreate,
    current_user: User = Depends(get_default_user)
):
    """Create a new pattern ignore"""
    pattern = await PatternIgnore.create(
        **pattern_ignore.model_dump(),
        user_id=current_user.id  # Use user_id instead of user
    )
    return await PatternIgnore.get(id=pattern.id)


@router.get("/", response_model=List[PatternIgnoreResponse])
async def get_pattern_ignores(current_user: User = Depends(get_default_user)):
    """Get all pattern ignores for the current user"""
    return await PatternIgnore.filter(user_id=current_user.id)


@router.get("/{pattern_id}", response_model=PatternIgnoreResponse)
async def get_pattern_ignore(
    pattern_id: int,
    current_user: User = Depends(get_default_user)
):
    """Get a specific pattern ignore by ID"""
    pattern = await PatternIgnore.filter(id=pattern_id, user_id=current_user.id).first()
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern ignore not found"
        )
    return pattern


@router.put("/{pattern_id}", response_model=PatternIgnoreResponse)
async def update_pattern_ignore(
    pattern_id: int,
    pattern_data: PatternIgnoreUpdate,
    current_user: User = Depends(get_default_user)
):
    """Update a pattern ignore"""
    pattern = await PatternIgnore.filter(id=pattern_id, user_id=current_user.id).first()
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern ignore not found"
        )
    
    update_data = {k: v for k, v in pattern_data.model_dump().items() if v is not None}
    if update_data:
        await PatternIgnore.filter(id=pattern_id).update(**update_data)
    
    return await PatternIgnore.get(id=pattern_id)


@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pattern_ignore(
    pattern_id: int,
    current_user: User = Depends(get_default_user)
):
    """Delete a pattern ignore"""
    pattern = await PatternIgnore.filter(id=pattern_id, user_id=current_user.id).first()
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern ignore not found"
        )
    
    await pattern.delete()
    return None
