from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from jose import jwt, JWTError
from strawberry.types import Info
from fastapi import Depends,HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db

from ..models.users import User
from ..config import settings
from ..crud.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso con un tiempo de expiración
    
    Args:
        data (Dict[str, Any]): Los datos a incluir en el token (normalmente el ID y email del usuario)
        expires_delta (Optional[timedelta], optional): Tiempo personalizado de expiración.
            Si no se proporciona, se usa el valor de settings.jwt_access_token_expire_minutes
    
    Returns:
        str: Token JWT firmado
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    # Añadir tiempo de expiración al payload
    to_encode.update({"exp": expire})
    
    # Codificar y firmar el token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de refresco con un tiempo de expiración más largo
    
    Args:
        data (Dict[str, Any]): Los datos a incluir en el token (normalmente solo el ID del usuario)
        expires_delta (Optional[timedelta], optional): Tiempo personalizado de expiración.
            Si no se proporciona, se usa el valor de settings.jwt_refresh_token_expire_days
    
    Returns:
        str: Token JWT firmado con mayor tiempo de expiración
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración (más largo para el refresh token)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    
    # Añadir tiempo de expiración al payload
    to_encode.update({"exp": expire})
    
    # Codificar y firmar el token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt

def get_current_user_from_context(info: Info) -> Optional[User]:
    """
    Extracts the authenticated user from the GraphQL context
    
    Args:
        info (Info): GraphQL resolver info object containing the context
        
    Returns:
        Optional[User]: The authenticated user or None if not authenticated
    """
    # Access the user from the context, which should have been set by authentication middleware
    context = info.context
    
    # Check if context has a user attribute
    if hasattr(context, 'user'):
        return context.user
    
    # If using a dict-like context, check for 'user' key
    if isinstance(context, dict) and 'user' in context:
        return context['user']
    
    # If using a request-based context, check for user in request state
    if hasattr(context, 'request') and hasattr(context.request, 'state'):
        if hasattr(context.request.state, 'user'):
            return context.request.state.user
    
    # No user found in context
    return None

def decode_token(token: str) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token (str): El token JWT a decodificar
        
    Returns:
        Dict[str, Any]: El payload decodificado del token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error decoding token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def get_user_from_token(db: Session, token: str) -> Optional[User]:
    """
    Obtiene un usuario a partir de un token JWT
    
    Args:
        db (Session): Sesión de base de datos
        token (str): Token JWT a verificar
        
    Returns:
        Optional[User]: El usuario si el token es válido, None en caso contrario
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return None
            
        user = get_user_by_id(db, int(user_id))
        return user
    except Exception:
        return None

def get_current_user_from_context(info) -> Optional[User]:
    """
    Helper para obtener el usuario actual desde el contexto de GraphQL
    
    Args:
        info: Información del contexto de GraphQL
        
    Returns:
        Optional[User]: Usuario autenticado o None
    """
    context = info.context
    return getattr(context, "user", None)

async def get_admin_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Verifica que el usuario actual sea un administrador.
    
    Args:
        token (str): Token JWT de autenticación
        db (Session): Sesión de base de datos
        
    Returns:
        User: El usuario administrador autenticado
        
    Raises:
        HTTPException: Si el usuario no está autenticado o no tiene permisos de administrador
    """
    # Primero verificar si el usuario está autenticado
    user = get_user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Luego verificar si el usuario es administrador
    # Esto depende de cómo estés modelando los roles de administrador
    # Por ejemplo, podrías tener un campo is_admin, o revisar por un rol específico
    
    # Opción 1: Si tienes un campo is_admin
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    # Opción 2: Si usas roles
    # admin_role = "ADMIN"  # O el identificador que uses para el rol de administrador
    # if not any(role.name == admin_role for role in user.roles):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Se requieren permisos de administrador"
    #     )
    
    return user