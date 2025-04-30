import strawberry
from strawberry.types import Info
from typing import Optional
from sqlalchemy.orm import Session

from ...database import get_db
from ..types.auth import AuthUserType
from ...auth.jwt import get_current_user_from_context
from ...models.user import User

@strawberry.type
class AuthQueries:
    @strawberry.field
    def me(self, info: Info) -> Optional[AuthUserType]:
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
            
    @strawberry.field
    def google_auth_url(self) -> str:
        """
        Get the Google OAuth2 authorization URL
        """
        from ...auth.oauth import get_google_auth_url
        return get_google_auth_url()