from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from ..database import get_db
from ..models.users import User
from ..services.auth_service import AuthService
from ..config import settings

# Configurar el esquema de seguridad Bearer
security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtiene el usuario actual desde el token JWT para endpoints FastAPI
    
    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extraer el token del esquema Bearer
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)
            
        # Usar el servicio de auth existente
        user = await AuthService.get_current_user(token_str, db)
        if not user:
            raise credentials_exception
            
        return user
        
    except JWTError:
        raise credentials_exception
    except Exception as e:
        print(f"Error en autenticación: {e}")
        raise credentials_exception