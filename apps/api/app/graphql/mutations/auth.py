from __future__ import annotations
import strawberry
from strawberry.types import Info
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ...database import get_db
from ..types.auth import TokenType, AuthUserType
# Actualizar importaciones
from ...services.auth_service import AuthService  # Nueva importación
from ...services.user_service import UserService  # Nueva importación


# Definir las funciones de mutación como resolvers independientes
async def google_auth(info: Info, code: str) -> TokenType:
    """
    Process Google OAuth2 authentication and return JWT tokens
    """
    db = next(get_db())
    
    try:
        # Reemplazar estos dos pasos:
        # user_data = await get_google_user(code)
        # db_user = create_user_oauth(db, user_data)
        
        # Por estos:
        user_info, token_info = await AuthService.get_google_user_and_tokens(code)
        db_user = await UserService.create_user_oauth(db, user_info)
        
        # Reemplazar estas llamadas:
        # access_token = create_access_token(data={"sub": str(db_user.id), "email": db_user.email})
        # refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
        
        # Por estas:
        access_token = await AuthService.create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email}
        )
        refresh_token = await AuthService.create_refresh_token(
            data={"sub": str(db_user.id)}
        )
        
        return TokenType(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")

async def refresh_token(info: Info, refresh_token: str) -> TokenType:
    """
    Use a refresh token to get a new access token
    """
    db = next(get_db())
    
    try:
        # Reemplazar:
        # payload = decode_token(refresh_token)
        
        # Por:
        payload = await AuthService.decode_token(refresh_token)
        
        user_id = payload.get("sub")
        
        if not user_id:
            raise Exception("Invalid refresh token")
            
        # Reemplazar:
        # user = get_user_by_id(db, int(user_id))
        
        # Por:
        user = await UserService.get_user_by_id(db, int(user_id))
        
        if not user:
            raise Exception("User not found")
            
        # Reemplazar:
        # new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        # new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Por:
        new_access_token = await AuthService.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        new_refresh_token = await AuthService.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return TokenType(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        raise Exception(f"Token refresh failed: {str(e)}")

async def logout(info: Info, token: str) -> bool:
    """
    Logout user (invalidate token)
    """
    # Reemplazar el comentario y la implementación simple
    # Por una llamada real al servicio:
    db = next(get_db())
    try:
        result = await AuthService.invalidate_token(token, db)
        return result.get("success", True)
    except Exception as e:
        raise Exception(f"Logout failed: {str(e)}")

# Mantener la clase AuthMutations para compatibilidad si ya está en uso
@strawberry.type
class AuthMutations:
    google_auth = strawberry.mutation(resolver=google_auth)
    refresh_token = strawberry.mutation(resolver=refresh_token)
    logout = strawberry.mutation(resolver=logout)