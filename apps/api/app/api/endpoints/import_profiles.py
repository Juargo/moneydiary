from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...database import get_db
from ...schemas.file_imports import (
    FileImportProfileCreate,
    FileImportProfileUpdate,
    FileImportProfileResponse,
    ImportHistoryResponse
)
from ...services.import_profile_service import (
    create_import_profile,
    get_user_import_profiles,
    get_user_import_profile,
    update_import_profile,
    delete_import_profile,
    get_import_history,
    create_default_profiles_for_popular_banks
)
from ...utils.fastapi_auth import get_current_user
from ...models.users import User

router = APIRouter()

@router.post("", response_model=FileImportProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile_endpoint(
    profile_data: FileImportProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea un nuevo perfil de importación"""
    try:
        new_profile = create_import_profile(db, current_user.id, profile_data)
        return FileImportProfileResponse.from_orm(new_profile)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error creating import profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("", response_model=List[FileImportProfileResponse])
async def get_profiles_endpoint(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene los perfiles de importación del usuario"""
    try:
        profiles = get_user_import_profiles(db, current_user.id, account_id)
        return [FileImportProfileResponse.from_orm(profile) for profile in profiles]
    except Exception as e:
        print(f"Error getting import profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{profile_id}", response_model=FileImportProfileResponse)
async def get_profile_endpoint(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un perfil específico"""
    profile = get_user_import_profile(db, current_user.id, profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de importación no encontrado"
        )
    
    return FileImportProfileResponse.from_orm(profile)

@router.put("/{profile_id}", response_model=FileImportProfileResponse)
async def update_profile_endpoint(
    profile_id: int,
    profile_data: FileImportProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza un perfil de importación"""
    try:
        updated_profile = update_import_profile(db, current_user.id, profile_id, profile_data)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de importación no encontrado"
            )
        
        return FileImportProfileResponse.from_orm(updated_profile)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error updating import profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_endpoint(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un perfil de importación"""
    success = delete_import_profile(db, current_user.id, profile_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de importación no encontrado"
        )

@router.post("/create-defaults", status_code=status.HTTP_201_CREATED)
async def create_default_profiles_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea perfiles por defecto para bancos populares"""
    try:
        create_default_profiles_for_popular_banks(db, current_user.id)
        return {"message": "Perfiles por defecto creados exitosamente"}
    except Exception as e:
        print(f"Error creating default profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/history", response_model=List[ImportHistoryResponse])
async def get_import_history_endpoint(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene el historial de importaciones"""
    try:
        history = get_import_history(db, current_user.id, limit, offset)
        return [ImportHistoryResponse(**item) for item in history]
    except Exception as e:
        print(f"Error getting import history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )