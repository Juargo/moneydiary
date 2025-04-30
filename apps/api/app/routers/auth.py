from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.oauth import get_google_auth_url, get_google_user_and_tokens
from ..auth.jwt import create_access_token, create_refresh_token
from ..crud.user import create_user_oauth
from ..config import settings

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.get("/google/login")
async def google_login():
    """Inicia el flujo OAuth2 con Google"""
    return RedirectResponse(get_google_auth_url())

@router.get("/google/callback")
async def google_callback(request: Request, code: str, db: Session = Depends(get_db)):
    """
    Procesa el callback de Google OAuth2
    
    Este endpoint recibe el código de autorización de Google después de que el usuario
    ha iniciado sesión y autorizado la aplicación. Intercambia este código por tokens
    de acceso, crea o actualiza el usuario en la base de datos, y redirige al frontend
    con los tokens JWT para autenticación.
    """
    try:
        # Obtener datos del usuario y tokens de Google
        oauth_data = await get_google_user_and_tokens(code)
        
        # Crear o actualizar usuario en la base de datos
        from datetime import datetime
        
        db_user = create_user_oauth(
            db=db,
            user_data=oauth_data["user_data"],
            token_data=oauth_data["token_data"]
        )
        
        # Actualizar fecha de último login
        db_user.last_login = datetime.utcnow()
        db.commit()
        
        # Crear tokens JWT para la autenticación en la API
        access_token = create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(db_user.id)}
        )
        
        # Redirigir al frontend con los tokens
        frontend_callback = f"{settings.frontend_url}{settings.frontend_auth_callback_path}"
        redirect_url = f"{frontend_callback}?access_token={access_token}&refresh_token={refresh_token}"
        
        return RedirectResponse(redirect_url)
        
    except Exception as e:
        # En caso de error, redirigir a la página de error
        error_url = f"{settings.frontend_url}{settings.frontend_auth_error_path}?error={str(e)}"
        return RedirectResponse(error_url)