from fastapi import Request
from sqlalchemy.orm import Session
import strawberry
from typing import Optional, Dict, Any

from ..database import get_db
from ..auth.jwt import get_user_from_token

class GraphQLContext:
    """
    Contexto para las operaciones GraphQL
    
    Esta clase proporciona acceso a:
    - La sesión de base de datos
    - El usuario autenticado actual (si hay un token válido)
    - La solicitud HTTP original
    """
    def __init__(self, db: Session, request: Request, user: Optional[Dict[str, Any]] = None):
        self.db = db
        self.request = request
        self.user = user

async def get_context(request: Request) -> GraphQLContext:
    """
    Crea y devuelve el contexto para las operaciones GraphQL
    
    Esta función:
    1. Obtiene una sesión de base de datos
    2. Intenta extraer y verificar el token de autenticación del header
    3. Si hay un token válido, obtiene el usuario correspondiente
    4. Devuelve un objeto de contexto con estos datos
    """
    # Obtener sesión de base de datos
    db = next(get_db())
    
    # Intentar obtener y verificar token de autenticación
    user = None
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            # Obtener usuario desde el token
            user = get_user_from_token(db, token)
        except Exception as e:
            # Si hay un error con el token, solo registramos y continuamos sin usuario
            print(f"Error al verificar token: {str(e)}")
    
    # Crear y devolver contexto
    return GraphQLContext(db=db, request=request, user=user)