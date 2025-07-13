from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import hashlib
import traceback
from typing import Dict, Any, Optional

from ..models.users import User
from ..models.role import Role
from ..crud.user import get_user_by_email, get_user_by_id

class UserService:
    @staticmethod
    async def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Busca un usuario por su correo electrónico
        """
        return get_user_by_email(db, email)
    
    @staticmethod
    async def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Busca un usuario por su ID
        """
        return get_user_by_id(db, user_id)
    
    @staticmethod
    async def create_user_oauth(db: Session, user_data: dict) -> User:
        """
        Crea o actualiza un usuario a partir de datos de OAuth
        
        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario devueltos por el proveedor OAuth
            
        Returns:
            User: Usuario creado o actualizado
        """
        try:
            # Verificar que el email existe
            if not user_data.get('email'):
                raise ValueError("El email es requerido para crear un usuario")
                
            # Buscar usuario existente por email
            db_user = await UserService.get_user_by_email(db, user_data["email"])
            
            # Si el usuario ya existe, actualizar sus datos
            if db_user:
                # Actualizar usuario existente
                db_user.name = user_data.get("name", db_user.name)
                db_user.profile_image = user_data.get("profile_image", db_user.profile_image)
                db_user.is_active = True
                db_user.last_login = datetime.now()
                 # Si el usuario no tiene rol, asignar el predeterminado
                if not db_user.role_id:
                    default_role = db.query(Role).filter(Role.name == "user").first()
                    if default_role:
                        db_user.role_id = default_role.id
                
                db.commit()
                db.refresh(db_user)
                return db_user
            else:
                # Crear nuevo usuario
                # Generar un hash seguro aleatorio para satisfacer la restricción NOT NULL
                random_password = secrets.token_hex(16)  # 32 caracteres aleatorios
                password_hash = hashlib.sha256(random_password.encode()).hexdigest()
                default_role = db.query(Role).filter(Role.name == "user").first()

                if not default_role:
                    raise ValueError("No se encontró el rol por defecto 'user'")
                # Crear nuevo usuario
                new_user = User(
                    email=user_data["email"],
                    name=user_data.get("name", ""),
                    profile_image=user_data.get("profile_image", ""),
                    is_active=True,
                    email_verified=user_data.get("email_verified", False),
                    password_hash=password_hash, 
                    last_login=datetime.now(),
                    role_id=default_role.id
                )

                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                return new_user
        except Exception as e:
            db.rollback()
            raise