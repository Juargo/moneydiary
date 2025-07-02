import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class Bank:
    id: int
    name: str
    code: str
    logo_url: Optional[str] = None
    active: bool = True
    description: Optional[str] = None
    created_at: str
    updated_at: str

def convert_bank_model_to_graphql(bank_model) -> Bank:
    """Convierte un modelo SQLAlchemy Bank a tipo GraphQL Bank"""
    return Bank(
        id=bank_model.id,
        name=bank_model.name,
        code=bank_model.code,
        logo_url=bank_model.logo_url,
        active=bank_model.active or True,
        description=bank_model.description,
        created_at=bank_model.created_at.isoformat() if bank_model.created_at else "",
        updated_at=bank_model.updated_at.isoformat() if bank_model.updated_at else ""
    )