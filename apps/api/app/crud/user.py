from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from ..models.users import User
from ..models.oauth2_token import OAuth2Token

def get_user_by_email(db: Session, email: str) -> User:
    """
    Busca un usuario por su correo electrónico
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Busca un usuario por su ID
    """
    return db.query(User).filter(User.id == user_id).first()

def create_oauth2_token(db: Session, user_id: int, provider: str, token_data: Dict[str, Any]) -> OAuth2Token:
    """
    Crea o actualiza un token OAuth2 para un usuario
    """
    # Buscar si ya existe un token para este usuario y proveedor
    db_token = db.query(OAuth2Token).filter(
        OAuth2Token.user_id == user_id,
        OAuth2Token.provider == provider
    ).first()
    
    expires_at = datetime.utcnow() + datetime.timedelta(seconds=token_data.get("expires_in", 3600))
    
    if db_token:
        # Actualizar token existente
        db_token.access_token = token_data["access_token"]
        db_token.refresh_token = token_data.get("refresh_token", db_token.refresh_token)
        db_token.expires_at = expires_at
        db_token.scope = token_data.get("scope", db_token.scope)
        db_token.updated_at = datetime.utcnow()
    else:
        # Crear nuevo token
        db_token = OAuth2Token(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            provider=provider,
            expires_at=expires_at,
            scope=token_data.get("scope")
        )
        db.add(db_token)
    
    db.commit()
    db.refresh(db_token)
    return db_token

def create_user_oauth(db: Session, user_data: dict) -> User:
    """
    Crea o actualiza un usuario a partir de datos de OAuth
    
    Args:
        db: Sesión de base de datos
        user_data: Datos del usuario devueltos por el proveedor OAuth
        
    Returns:
        User: Usuario creado o actualizado
    """
    try:
        print(f"Procesando usuario OAuth con email: {user_data.get('email', 'NO EMAIL')}")
        
        # Verificar que el email existe
        if not user_data.get('email'):
            raise ValueError("El email es requerido para crear un usuario")
            
        # Buscar usuario existente por email
        db_user = get_user_by_email(db, user_data["email"])
        
        if db_user:
            # Actualizar usuario existente
            db_user.name = user_data.get("name", db_user.name)
            db_user.profile_image = user_data.get("profile_image", db_user.profile_image)
            db_user.provider = user_data.get("provider", db_user.provider)
            db_user.provider_user_id = user_data.get("provider_user_id", db_user.provider_user_id)
            db_user.is_active = True
            db_user.last_login = datetime.now()
            
            db.commit()
            db.refresh(db_user)
            print(f"Usuario actualizado: ID={db_user.id}, Email={db_user.email}")
            return db_user
        else:
            # Crear nuevo usuario
            new_user = User(
                email=user_data["email"],
                name=user_data.get("name", ""),
                profile_image=user_data.get("profile_image", ""),
                provider=user_data.get("provider", "google"),
                provider_user_id=user_data.get("provider_user_id", ""),
                is_active=True,
                email_verified=user_data.get("email_verified", False),
                last_login=datetime.now()
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"Nuevo usuario creado: ID={new_user.id}, Email={new_user.email}")
            return new_user
    except Exception as e:
        db.rollback()
        print(f"Error al crear/actualizar usuario OAuth: {str(e)}")
        raise