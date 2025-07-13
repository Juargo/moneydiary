from __future__ import annotations
from strawberry.types import Info
from fastapi import HTTPException, status
from typing import Optional

from ..services.auth_service import AuthService
from ..models.users import User

async def get_authenticated_user(info: Info) -> User:
    """
    Extrae el token JWT del header Authorization y obtiene el usuario autenticado
    
    Args:
        info: Info de GraphQL que contiene la request
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        Exception: Si no hay token o es inválido
    """
    try:
        # Obtener la request desde el contexto de GraphQL
        request = info.context.request
        
        # Extraer el token del header Authorization
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise Exception("Token de autorización requerido")
        
        # Verificar que el header tenga el formato correcto
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            raise Exception("Esquema de autorización inválido. Use 'Bearer <token>'")
        
        if not token:
            raise Exception("Token no proporcionado")
        
        # Obtener la sesión de base de datos del contexto
        db = info.context.db
        
        # Usar AuthService para obtener el usuario autenticado
        current_user = await AuthService.get_current_user(token, db)
        
        if not current_user:
            raise Exception("Usuario no autenticado")
        
        return current_user
        
    except HTTPException as e:
        raise Exception(f"Error de autenticación: {e.detail}")
    except Exception as e:
        raise Exception(str(e))