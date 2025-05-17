from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from ...database import get_db
from ...services.bank_service import BankService
from ...models.banks import Bank
from ...auth.jwt import get_admin_user  

# Schemas (definidos inline por simplicidad, idealmente se deberían mover a un módulo de schemas)
from pydantic import BaseModel

class BankBase(BaseModel):
    name: str
    logo_url: str = None
    website: str = None
    description: str = None

class BankCreate(BankBase):
    pass

class BankUpdate(BankBase):
    name: str = None

class BankResponse(BankBase):
    id: int
    
    class Config:
        orm_mode = True

# Router - Ahora explícitamente para bancos del sistema
router = APIRouter(
    prefix="/system/banks",  # Prefijo modificado para indicar que son bancos del sistema
    tags=["system-banks"],   # Tag modificado para claridad
    responses={404: {"description": "Banco no encontrado"}},
)

@router.get("/", response_model=List[BankResponse])
async def read_system_banks(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    admin_user: Any = Depends(get_admin_user) 
):
    """Obtener todos los bancos del sistema"""
    banks = await BankService.get_banks(db, skip=skip, limit=limit)
    return banks

@router.get("/{bank_id}", response_model=BankResponse)
async def read_system_bank(
    bank_id: int, 
    db: AsyncSession = Depends(get_db),
    admin_user: Any = Depends(get_admin_user) 
):
    """Obtener un banco del sistema por su ID"""
    bank = await BankService.get_bank(db, bank_id=bank_id)
    return bank

# Las operaciones de escritura requieren permisos de administrador
@router.post("/", response_model=BankResponse, status_code=status.HTTP_201_CREATED)
async def create_system_bank(
    bank_data: BankCreate, 
    db: AsyncSession = Depends(get_db),
    admin_user: Any = Depends(get_admin_user)  # Solo administradores pueden crear bancos del sistema
):
    """Crear un nuevo banco en el sistema"""
    bank = await BankService.create_bank(db, bank_data.dict())
    return bank

@router.patch("/{bank_id}", response_model=BankResponse)
async def update_system_bank(
    bank_id: int,
    bank_data: BankUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: Any = Depends(get_admin_user)  # Solo administradores pueden actualizar bancos del sistema
):
    """Actualizar un banco existente en el sistema"""
    # Filtrar campos None para no actualizar campos que no se enviaron
    update_data = {k: v for k, v in bank_data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar"
        )
    
    updated_bank = await BankService.update_bank(db, bank_id, update_data)
    return updated_bank

@router.delete("/{bank_id}", response_model=Dict[str, bool])
async def delete_system_bank(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: Any = Depends(get_admin_user)  # Solo administradores pueden eliminar bancos del sistema
):
    """Eliminar un banco del sistema"""
    result = await BankService.delete_bank(db, bank_id)
    return result