from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

# Importar CRUD y modelos
from app.crud.user import get_user_by_id, get_users, create_user, update_user, delete_user
from app.models.users import User
from app.models.role import Role
from app.auth.jwt import create_access_token, verify_password, get_password_hash

class UserService:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User:
        """Obtiene un usuario por su ID con lógica de negocio adicional"""
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    
    @staticmethod
    async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene todos los usuarios con paginación"""
        return await get_users(db, skip=skip, limit=limit)
    
    @staticmethod
    async def create_new_user(db: AsyncSession, user_data: Dict[str, Any]) -> User:
        """Crea un nuevo usuario con validaciones de negocio"""
        # Validar datos según reglas de negocio
        if len(user_data.get("password", "")) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        
        # Hashear contraseña
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        # Crear usuario
        return await create_user(db, user_data)
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Dict[str, Any]:
        """Autenticar usuario y generar token"""
        # Lógica de autenticación
        user = await get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        # Generar token
        access_token = create_access_token(data={"sub": user.username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "roles": [role.name for role in user.roles]
            }
        }