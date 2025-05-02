from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import requests
import traceback
from urllib.parse import urlencode

from ...database import get_db
from ...auth.oauth import get_google_auth_url, get_google_user_and_tokens
from ...auth.jwt import create_access_token, create_refresh_token
from ...crud.user import create_user_oauth, get_user_by_email, get_user_by_id
from ...config import settings

router = APIRouter()

@router.get("/google/login")
async def login_google():
    """
    Endpoint para iniciar el flujo de autenticación con Google OAuth2
    
    Redirige al usuario a la página de autenticación de Google
    """
    auth_url = get_google_auth_url()
    return RedirectResponse(auth_url)

@router.get("/google/callback")
async def google_callback(request: Request, code: str = None, error: str = None, db: Session = Depends(get_db)):
    """
    Endpoint de callback para el flujo de autenticación de Google
    """
    # Si hay un error en la autenticación de Google
    if error:
        error_encoded = urlencode({'message': f"Error de Google: {error}"})
        redirect_url = f"{settings.frontend_url}{settings.frontend_auth_error_path}?error={error_encoded}"
        return RedirectResponse(redirect_url)
    
    # Si no hay código, es un error
    if not code:
        error_encoded = urlencode({'message': "No se recibió código de autorización"})
        redirect_url = f"{settings.frontend_url}{settings.frontend_auth_error_path}?error={error_encoded}"
        return RedirectResponse(redirect_url)
    
    try:
        # Obtener información del usuario y tokens de Google
        user_info, token_info = await get_google_user_and_tokens(code)
        
        # Crear o actualizar usuario en nuestra base de datos
        db_user = create_user_oauth(db, user_info)
        
        # Generar tokens JWT para nuestra aplicación
        access_token = create_access_token(data={"sub": str(db_user.id), "email": db_user.email})
        refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
        
        # Preparar URL de redirección con tokens
        query_params = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

        print(f"FRONTEND URL: {settings.frontend_url}")
        print(f"CALLBACK PATH: {settings.frontend_auth_callback_path}")
        print(f"QUERY PARAMS: {query_params}")


        redirect_url = f"{settings.frontend_url}{settings.frontend_auth_callback_path}?{urlencode(query_params)}"
        print(f"SUCCESS REDIRECT: {redirect_url}")

        # Redirigir al frontend
        return RedirectResponse(redirect_url)
        
    except Exception as e:
        # Si hay algún error, redirigir con mensaje de error detallado
        error_message = str(e)
        error_type = type(e).__name__
        error_details = {
            'message': f"Error de autenticación: {error_message}",
            'type': error_type,
            'details': traceback.format_exc()
        }
        
        # Log del error para depuración del servidor
        print(f"ERROR DE AUTENTICACIÓN: {error_type}: {error_message}")
        print(f"DETALLES: {traceback.format_exc()}")
        
        error_encoded = urlencode({'message': error_message})
        redirect_url = f"{settings.frontend_url}{settings.frontend_auth_error_path}?error={error_encoded}"
        return RedirectResponse(redirect_url)
    
@router.post("/refresh-token")
async def refresh_token_endpoint(refresh_token: str, db: Session = Depends(get_db)):
    """
    Endpoint para renovar tokens JWT usando un refresh token
    
    Returns:
        dict: Nuevos tokens de acceso y refresco
    """
    from ...auth.jwt import decode_token
    
    try:
        # Verificar el refresh token
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Obtener el usuario
        user = get_user_by_id(db, int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Generar nuevos tokens
        new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout():
    """
    Endpoint para cerrar sesión
    
    En una implementación completa, aquí podrías:
    1. Agregar el token a una lista negra
    2. Invalidar sesiones en base de datos
    3. Realizar otras acciones de limpieza
    
    Por ahora, simplemente devolvemos un mensaje de éxito
    """
    return {"message": "Successfully logged out"}