import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class TokenType:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@strawberry.type
class AuthUserType:
    id: int
    email: str
    name: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool
    created_at: datetime