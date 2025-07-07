from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import requests
from urllib.parse import urlencode

from ..database import get_db
from ..models.users import User
from ..models.invalidated_token import InvalidatedToken
from ..config import settings
from .user_service import UserService

# Reutilizar el OAuth2PasswordBearer existente
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

class AuthService:
    @staticmethod
    async def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT de acceso
        
        Args:
            data (Dict[str, Any]): Los datos a incluir en el token (normalmente sub con el ID de usuario)
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
    
    @staticmethod
    async def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT de refresco con un tiempo de expiración más largo
        """
        to_encode = data.copy()
        
        # Establecer tiempo de expiración (más largo para el refresh token)
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
        
        to_encode.update({"exp": expire})
        
        # Codificar y firmar el token
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    async def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodifica un token JWT sin verificar su validez
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Dict[str, Any]: Payload del token decodificado
        """
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        Obtiene el usuario actual a partir del token JWT
        
        Args:
            token: Token JWT de autorización
            db: Sesión de base de datos
            
        Returns:
            User: Usuario autenticado
            
        Raises:
            HTTPException: Si el token es inválido o expiró
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decodificar el token
            payload = await AuthService.decode_token(token)
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise credentials_exception
                
            # Obtener el usuario
            user = await UserService.get_user_by_id(db, int(user_id))
            if user is None:
                raise credentials_exception
                
            return user
            
        except Exception:
            raise credentials_exception
    
    @staticmethod
    async def get_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        Verifica que el usuario actual sea un administrador
        
        Args:
            token: Token JWT de autenticación
            db: Sesión de base de datos
            
        Returns:
            User: Usuario administrador autenticado
            
        Raises:
            HTTPException: Si el usuario no es administrador
        """
        user = await AuthService.get_current_user(token, db)
        
        # Verificar si el usuario es administrador
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador"
            )
            
        return user
    
    @staticmethod
    async def get_google_auth_url() -> str:
        """
        Genera la URL para autenticación OAuth2 con Google
        
        Returns:
            str: URL de redirección a Google Auth
        """
        # Parámetros para la solicitud de autorización
        auth_params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope":  " ".join(settings.GOOGLE_AUTH_SCOPES_LIST),
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account"
        }
        
        # Construir la URL
        auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(auth_params)}"
        return auth_url
    
    @staticmethod
    async def get_google_user_and_tokens(code: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Intercambia el código de autorización por tokens y obtiene info del usuario
        
        Args:
            code: Código de autorización de Google
            
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: Información del usuario y tokens
        """
        # Obtener tokens de acceso y refresco
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.google_redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Obtener información del usuario
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {token_info['access_token']}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
        
        # Formatear la información del usuario para nuestro sistema
        processed_user_info = {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "profile_image": user_info.get("picture"),
            "email_verified": user_info.get("email_verified", False),
            "provider": "google",
            "provider_user_id": user_info.get("sub")
        }
        
        return processed_user_info, token_info