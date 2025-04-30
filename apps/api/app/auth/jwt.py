from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt, JWTError

from ..config import settings

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