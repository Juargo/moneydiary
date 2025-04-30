import requests
from datetime import datetime
from fastapi import HTTPException, status
from typing import Dict, Any, Tuple

from ..config import settings

def get_google_auth_url() -> str:
    """
    Genera la URL de autorización de OAuth2 de Google
    
    Esta URL es donde se redirigirá al usuario para que inicie sesión con Google
    y otorgue los permisos solicitados a la aplicación.
    
    Returns:
        str: URL completa para iniciar el flujo de OAuth2 con Google
    """
    # Convertir la cadena de scopes (separados por comas) a una lista y luego unirlos con '+'
    # para el formato que requiere la URL de autorización
    scopes = "+".join(settings.google_auth_scopes.split(","))
    
    # Construir la URL de autorización con todos los parámetros necesarios
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code"
        f"&client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&scope={scopes}"
        f"&access_type=offline"  # Para obtener refresh_token
        f"&prompt=consent"  # Para asegurar que siempre se pida consentimiento y obtener refresh_token
    )
    
    return google_auth_url

def get_google_user_and_tokens(code: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Intercambia el código de autorización por tokens y obtiene información del usuario
    
    Esta función realiza dos pasos:
    1. Intercambia el código de autorización por tokens de acceso/refresco
    2. Usa el token de acceso para obtener información del perfil del usuario
    
    Args:
        code (str): Código de autorización recibido de Google
        
    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: Tuple con datos del usuario y tokens
        
    Raises:
        HTTPException: Si ocurre un error en alguna de las peticiones a Google
    """
    # Paso 1: Intercambiar el código por tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener tokens de Google: {str(e)}"
        )
    
    # Paso 2: Obtener información del usuario con el token de acceso
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {token_json['access_token']}"}
    
    try:
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_data = userinfo_response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener información del usuario de Google: {str(e)}"
        )
    
    # Estructurar datos del usuario
    user_info = {
        "email": user_data["email"],
        "name": user_data.get("name"),
        "profile_image": user_data.get("picture"),
        "provider": "google",
        "provider_user_id": user_data["id"],
        "email_verified": user_data.get("verified_email", False)
    }
    
    # Estructurar datos de token
    token_info = {
        "access_token": token_json["access_token"],
        "refresh_token": token_json.get("refresh_token"),
        "expires_in": token_json.get("expires_in", 3600),
        "scope": token_json.get("scope")
    }
    
    return user_info, token_info

# Para compatibilidad con el código existente que espera get_google_user
def get_google_user(code: str) -> Dict[str, Any]:
    """
    Obtiene información del usuario de Google utilizando un código de autorización.
    
    Esta función es un wrapper para get_google_user_and_tokens que solo devuelve 
    la información del usuario.
    
    Args:
        code (str): Código de autorización de Google OAuth2
        
    Returns:
        Dict[str, Any]: Información del usuario
    """
    user_info, _ = get_google_user_and_tokens(code)
    return user_info