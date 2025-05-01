import requests
from datetime import datetime
from fastapi import HTTPException, status
from typing import Dict, Any, Tuple

from ..config import settings

def get_google_auth_url() -> str:
    """
    Genera la URL de autorización de OAuth2 de Google
    """
    # Usar espacio como separador y luego codificar URL
    from urllib.parse import quote_plus
    
    # Los scopes deben estar separados por espacios según la especificación de OAuth2
    scopes = " ".join(settings.GOOGLE_AUTH_SCOPES_LIST)
    encoded_scopes = quote_plus(scopes)
    
    # Construir la URL de autorización con todos los parámetros necesarios
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code"
        f"&client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&scope={encoded_scopes}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
   # Log para depuración detallada
    print(f"URL de autorización de Google: {google_auth_url}")
    print(f"Client ID: {settings.google_client_id}")
    print(f"Redirect URI: {settings.google_redirect_uri}")
    print(f"Scopes solicitados: {settings.GOOGLE_AUTH_SCOPES_LIST}")
    print(f"Scopes codificados: {encoded_scopes}")

    return google_auth_url

async def get_google_user_and_tokens(code: str):
    """
    Intercambia el código de autorización por tokens y obtiene información del usuario
    """
    token_url = "https://oauth2.googleapis.com/token"
    
    print(f"Realizando solicitud de token a Google con código: {code[:10]}...")
    print(f"Redirect URI: {settings.google_redirect_uri}")
    print(f"Client ID: {settings.google_client_id[:10]}...")
    
    token_data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    
    # Usar headers explícitos para asegurar formato correcto
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            print(f"Error en la respuesta del token: {token_response.status_code}")
            print(f"Respuesta de error: {token_response.text}")
            token_response.raise_for_status()
            
        token_json = token_response.json()
        print("Token obtenido exitosamente")
        
        # Verificar qué ámbitos (scopes) fueron aprobados
        if 'scope' in token_json:
            print(f"Ámbitos aprobados: {token_json['scope']}")
            if 'email' not in token_json['scope']:
                print("ADVERTENCIA: El ámbito 'email' no fue aprobado")
        

         # Cambia a la API v3
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_data = userinfo_response.json()
        
         # Imprimir la respuesta completa para depuración
        print(f"Respuesta completa de userinfo: {user_data}")
        
         # Diferentes APIs de Google pueden usar nombres de campos distintos
        email = user_data.get("email") or user_data.get("emails", [{}])[0].get("value")
        
        if not email:
            # Intenta otro endpoint si el email no está disponible
            try:
                people_api_url = "https://people.googleapis.com/v1/people/me?personFields=emailAddresses"
                people_response = requests.get(people_api_url, headers=headers)
                people_response.raise_for_status()
                people_data = people_response.json()
                
                print(f"Respuesta de People API: {people_data}")
                
                # Intenta extraer el email de la People API
                if "emailAddresses" in people_data and people_data["emailAddresses"]:
                    email = people_data["emailAddresses"][0].get("value")
            except Exception as people_error:
                print(f"Error al usar People API: {str(people_error)}")
        
        # Si aún no hay email, usar un identificador alternativo
        if not email:
            user_id = user_data.get("id") or user_data.get("sub")
            if user_id:
                email = f"{user_id}@placeholder.oauth.google"
                print(f"Usando email placeholder basado en ID: {email}")
            else:
                raise Exception("No se pudo obtener un identificador de usuario válido")
        
        # Crear estructura de datos del usuario
        user_info = {
            "email": email,
            "name": user_data.get("name", user_data.get("given_name", "")),
            "profile_image": user_data.get("picture", ""),
            "provider": "google",
            "provider_user_id": user_data.get("id", user_data.get("sub", "")),
            "email_verified": user_data.get("verified_email", user_data.get("email_verified", False))
        }
        
        print(f"Datos de usuario procesados: {user_info}")
        
        # Estructura de tokens
        token_info = {
            "access_token": token_json["access_token"],
            "refresh_token": token_json.get("refresh_token", ""),
            "expires_in": token_json.get("expires_in", 3600),
            "token_type": token_json.get("token_type", "Bearer")
        }

        # Al final de la función get_google_user_and_tokens
        if not user_info["name"]:
            # Intenta usar el ID como nombre si no hay nombre disponible
            user_info["name"] = f"Usuario {user_info['provider_user_id'][:8]}"

        # Registra que estamos usando un email placeholder
        if "@placeholder.oauth.google" in user_info["email"]:
            print("NOTA: Usando email placeholder porque Google no proporcionó el email real")
            print("Esto es normal en algunas configuraciones de OAuth o si el usuario no otorgó permiso de email")

        return user_info, token_info
        
    except Exception as e:
        print(f"Error en get_google_user_and_tokens: {str(e)}")
        raise

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