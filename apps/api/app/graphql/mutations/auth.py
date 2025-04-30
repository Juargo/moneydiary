import strawberry
from strawberry.types import Info
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ...database import get_db
from ..types.auth import TokenType, AuthUserType
from ...auth.oauth import get_google_user
from ...auth.jwt import decode_token, create_access_token, create_refresh_token
from ...crud.user import create_user_oauth, get_user_by_id

# Definir las funciones de mutación como resolvers independientes
async def google_auth(info: Info, code: str) -> TokenType:
    """
    Process Google OAuth2 authentication and return JWT tokens
    """
    db = next(get_db())
    
    try:
        # Get user data from Google
        user_data = await get_google_user(code)
        
        # Create or update user in database
        db_user = create_user_oauth(db, user_data)
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email}
        )
        refresh_token = create_refresh_token(
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
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise Exception("Invalid refresh token")
            
        # Get user
        user = get_user_by_id(db, int(user_id))
        if not user:
            raise Exception("User not found")
            
        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return TokenType(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        raise Exception(f"Token refresh failed: {str(e)}")

async def logout(info: Info) -> bool:
    """
    Logout user (invalidate token)
    """
    # Aquí podrías implementar lógica para invalidar tokens si mantienes una lista negra
    # de tokens revocados o una tabla en la base de datos
    # Por ahora, simplemente devolvemos True para indicar éxito
    return True

# Mantener la clase AuthMutations para compatibilidad si ya está en uso
@strawberry.type
class AuthMutations:
    google_auth = strawberry.mutation(resolver=google_auth)
    refresh_token = strawberry.mutation(resolver=refresh_token)
    logout = strawberry.mutation(resolver=logout)