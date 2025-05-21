from fastapi import Request
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext
from typing import Optional, Dict, Any, Union, List
from sqlalchemy.orm.decl_api import DeclarativeMeta
import logging

from ..database import get_db
from ..services.auth_service import AuthService
from .case_converter import snake_to_camel_case

# Configure logging
logger = logging.getLogger(__name__)

class GraphQLContext(BaseContext):
    """
    Contexto para las operaciones GraphQL
    
    Esta clase proporciona acceso a:
    - La sesión de base de datos
    - El usuario autenticado actual (si hay un token válido)
    - La solicitud HTTP original
    """
    def __init__(self, db: Session, request: Request, user: Optional[Any] = None):
        super().__init__()  # Important: call the parent constructor
        self.db = db
        self.request = request
        
        # Process user data
        if user:
            try:
                self.user = self._prepare_user(user)
                # Add debugging information
                logger.debug(f"Prepared user data for GraphQL: {self.user}")
            except Exception as e:
                logger.error(f"Error preparing user data: {str(e)}")
                self.user = None
        else:
            self.user = None

    # El resto de métodos de la clase permanecen igual
    def _prepare_user(self, user: Any) -> Dict[str, Any]:
        """
        Prepara el objeto usuario para ser utilizado en GraphQL
        
        Si el usuario es un modelo SQLAlchemy, lo convierte a un diccionario
        y luego convierte las claves de snake_case a camelCase
        """
        logger.debug(f"Preparing user for GraphQL, type: {type(user)}")
        
        # Convert SQLAlchemy model to dict if needed
        if hasattr(user, '__mapper__'):  # Check if it's a SQLAlchemy model
            logger.debug(f"Converting SQLAlchemy model to dict")
            # Get all column attributes
            user_dict = {}
            for column in user.__mapper__.columns:
                user_dict[column.key] = getattr(user, column.key)
            
            logger.debug(f"SQLAlchemy model converted to dict with fields: {list(user_dict.keys())}")
            
            # Convert to camelCase
            result = self._convert_to_camel_case(user_dict)
            logger.debug(f"Converted to camelCase with fields: {list(result.keys())}")
            return result
        elif isinstance(user, dict):
            logger.debug(f"User is already a dict with fields: {list(user.keys())}")
            result = self._convert_to_camel_case(user)
            logger.debug(f"Converted dict to camelCase with fields: {list(result.keys())}")
            return result
            
        # Return as is if it's not a model or dict
        logger.debug(f"User is not a SQLAlchemy model or dict, returning as is")
        return user

    def _convert_to_camel_case(self, data: Any) -> Any:
        """
        Convierte recursivamente las claves de diccionarios de snake_case a camelCase,
        procesa listas y diccionarios anidados
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Skip keys that start with underscore
                if isinstance(key, str) and key.startswith('_'):
                    result[key] = self._convert_to_camel_case(value)
                    continue
                    
                if isinstance(key, str) and '_' in key:
                    # Convert snake_case to camelCase
                    components = key.split('_')
                    camel_key = components[0] + ''.join(x.title() for x in components[1:])
                    result[camel_key] = self._convert_to_camel_case(value)
                else:
                    result[key] = self._convert_to_camel_case(value)
            return result
        elif isinstance(data, list):
            return [self._convert_to_camel_case(item) for item in data]
        else:
            return data

    def convert_field_name(self, field_name: str) -> str:
        """
        Utility method to convert field names according to GraphQL conventions
        """
        return snake_to_camel_case(field_name) if '_' in field_name else field_name

async def get_context(request: Request) -> GraphQLContext:
    """
    Crea y devuelve el contexto para las operaciones GraphQL
    
    Esta función:
    1. Obtiene una sesión de base de datos
    2. Intenta extraer y verificar el token de autenticación del header
    3. Si hay un token válido, obtiene el usuario correspondiente
    4. Devuelve un objeto de contexto con estos datos
    """
    # Log request info
    logger.debug(f"Creating GraphQL context for request: {request.method} {request.url.path}")
    logger.debug(f"Request headers: {request.headers}")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    # Intentar obtener y verificar token de autenticación
    user = None
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            # Cambiar este código:
            # user = get_user_from_token(db, token)
            # Por este:
            user = await AuthService.get_current_user(token, db)
            logger.debug(f"User from token: {user}, type: {type(user)}")
        except Exception as e:
            # Si hay un error con el token, solo registramos y continuamos sin usuario
            logger.error(f"Error al verificar token: {str(e)}")
    
    # Crear y devolver contexto
    return GraphQLContext(db=db, request=request, user=user)