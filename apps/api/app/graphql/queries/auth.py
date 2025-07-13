from __future__ import annotations
import strawberry
from strawberry.types import Info
from typing import Optional
from sqlalchemy.orm import Session

from ...database import get_db
from ..types.auth import AuthUserType
# Actualizar importación de JWT a AuthService
from ...services.auth_service import AuthService
from ...models.users import User

from ..types.auth import RoleType, PermissionType

async def get_me(root, info: Info) -> Optional[AuthUserType]:
    """
    Get the current authenticated user
    """
    context = info.context
    
    # Verificar si hay un usuario en el contexto
    if not hasattr(context, 'user') or context.user is None:
        return None
    
    user = context.user
    
    # Obtener roles y permisos si están disponibles
    role = None
    permissions = []
    
    if hasattr(user, 'role') and user.role:
        # Convertir el rol a RoleType
        role_permissions = []
        if hasattr(user.role, 'permissions'):
            role_permissions = [
                PermissionType(
                    id=perm.id,
                    name=perm.name,
                    resource=perm.resource,
                    action=perm.action,
                    description=perm.description
                ) for perm in user.role.permissions
            ]
        
        role = RoleType(
            id=user.role.id,
            name=user.role.name,
            description=user.role.description,
            permissions=role_permissions
        )
    
    # Obtener permisos directos del usuario si están disponibles
    if hasattr(user, 'permissions'):
        permissions = [
            PermissionType(
                id=perm.id,
                name=perm.name,
                resource=perm.resource,
                action=perm.action,
                description=perm.description
            ) for perm in user.permissions
        ]
        
    return AuthUserType(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_image=user.profile_image,
        active=user.active,
        email_verified=getattr(user, 'email_verified', False),
        created_at=getattr(user, 'created_at', None),
        role=role,
        permissions=permissions
    )

async def get_google_auth_url(root, info: Info) -> str:
    """
    Get the Google OAuth2 authorization URL
    """
    # Reemplazar la importación y llamada:
    # from ...auth.oauth import get_google_auth_url as get_url
    # return get_url()
    
    # Por:
    return await AuthService.get_google_auth_url()

# Mantener la clase AuthQueries para compatibilidad si ya está en uso en otros lugares
@strawberry.type
class AuthQueries:
    me = strawberry.field(resolver=get_me)
    google_auth_url = strawberry.field(resolver=get_google_auth_url)