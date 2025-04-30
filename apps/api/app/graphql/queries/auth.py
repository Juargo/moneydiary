import strawberry
from strawberry.types import Info
from typing import Optional
from sqlalchemy.orm import Session

from ...database import get_db
from ..types.auth import AuthUserType
from ...auth.jwt import get_current_user_from_context
from ...models.users import User

def get_me(root, info: Info) -> Optional[AuthUserType]:
    """
    Get the current authenticated user
    """
    # This gets the current user from the GraphQL context
    # which will be populated by the authentication middleware
    user = get_current_user_from_context(info)
    
    if not user:
        return None
        
    return AuthUserType(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_image=user.profile_image,
        is_active=user.is_active,
        created_at=user.created_at
    )

def get_google_auth_url(root, info: Info) -> str:
    """
    Get the Google OAuth2 authorization URL
    """
    from ...auth.oauth import get_google_auth_url as get_url
    return get_url()

# Mantener la clase AuthQueries para compatibilidad si ya está en uso en otros lugares
@strawberry.type
class AuthQueries:
    me = strawberry.field(resolver=get_me)
    google_auth_url = strawberry.field(resolver=get_google_auth_url)