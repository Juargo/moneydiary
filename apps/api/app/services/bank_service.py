from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from graphql import GraphQLError

# Importar el modelo de banco
from ..models.banks import Bank

class BankService:
    @staticmethod
    async def get_banks(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Bank]:
        """Obtener todos los bancos con paginación"""
        try:
            query = db.query(Bank).offset(skip).limit(limit)
            return await db.execute(query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener bancos: {str(e)}")

    @staticmethod
    async def get_bank(db: AsyncSession, bank_id: int) -> Optional[Bank]:
        """Obtener un banco por su ID"""
        try:
            bank = await db.get(Bank, bank_id)
            if not bank:
                raise HTTPException(status_code=404, detail="Banco no encontrado")
            return bank
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener banco: {str(e)}")

    @staticmethod
    async def create_bank(db: AsyncSession, bank_data: Dict[str, Any]) -> Bank:
        """Crear un nuevo banco"""
        try:
            # Validaciones de negocio
            if not bank_data.get("name"):
                raise ValueError("El nombre del banco es obligatorio")
                
            # Verificar si ya existe un banco con el mismo nombre
            query = db.query(Bank).filter(Bank.name == bank_data["name"])
            existing_bank = await db.execute(query)
            if existing_bank.first():
                raise ValueError(f"Ya existe un banco con el nombre '{bank_data['name']}'")
            
            # Crear el banco
            bank = Bank(**bank_data)
            db.add(bank)
            await db.commit()
            await db.refresh(bank)
            return bank
        except ValueError as e:
            # Propagar errores de validación para que los maneje la API
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear banco: {str(e)}")

    @staticmethod
    async def update_bank(db: AsyncSession, bank_id: int, bank_data: Dict[str, Any]) -> Bank:
        """Actualizar un banco existente"""
        try:
            bank = await BankService.get_bank(db, bank_id)
            
            # Actualizar atributos
            for key, value in bank_data.items():
                if hasattr(bank, key):
                    setattr(bank, key, value)
            
            await db.commit()
            await db.refresh(bank)
            return bank
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al actualizar banco: {str(e)}")

    @staticmethod
    async def delete_bank(db: AsyncSession, bank_id: int) -> Dict[str, bool]:
        """Eliminar un banco"""
        try:
            bank = await BankService.get_bank(db, bank_id)
            
            # Verificar dependencias antes de eliminar
            # Ejemplo: verificar si hay cuentas asociadas a este banco
            # (implementar esta lógica según tu modelo de datos)
            
            await db.delete(bank)
            await db.commit()
            return {"success": True}
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al eliminar banco: {str(e)}")

    # Método auxiliar para usar en GraphQL que convierte las excepciones HTTP a GraphQL
    @staticmethod
    def handle_graphql_error(func):
        """Decorador para convertir excepciones HTTP a GraphQL"""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                raise GraphQLError(e.detail, extensions={"code": e.status_code})
            except Exception as e:
                raise GraphQLError(str(e))
        return wrapper