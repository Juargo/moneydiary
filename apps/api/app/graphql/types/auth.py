import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class PermissionType:
    id: int
    name: str
    resource: str
    action: str
    description: Optional[str] = None

@strawberry.type
class RoleType:
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionType] = strawberry.field(default_factory=list)

@strawberry.type
class AuthUserType:
    id: int
    email: str
    name: Optional[str] = None
    profile_image: Optional[str] = None
    active: bool = True
    email_verified: Optional[bool] = False
    created_at: Optional[datetime] = None
    role: Optional[RoleType] = None
    permissions: List[PermissionType] = strawberry.field(default_factory=list)

@strawberry.type
class TokenType:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"