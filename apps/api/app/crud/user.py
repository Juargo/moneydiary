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

def create_user_oauth(db: Session, user_data: Dict[str, Any], token_data: Dict[str, Any] = None) -> User:
    """
    Crea un nuevo usuario a partir de datos de OAuth2 o actualiza uno existente
    
    Args:
        db (Session): Sesión de base de datos
        user_data (Dict[str, Any]): Datos del usuario obtenidos del proveedor OAuth
        token_data (Dict[str, Any], optional): Datos de token OAuth2. Defaults to None.
        
    Returns:
        User: El usuario creado o actualizado
    """
    # Verificar si el usuario ya existe por correo electrónico
    db_user = get_user_by_email(db, email=user_data["email"])
    
    if db_user:
        # Actualizar información del usuario existente
        if user_data.get("name") and not db_user.name:
            db_user.name = user_data["name"]
        
        if user_data.get("profile_image"):
            db_user.profile_image = user_data["profile_image"]
        
        # Marcar el correo como verificado si viene de OAuth2
        db_user.email_verified = True
        
        # Actualizar fecha de último acceso
        db_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_user)
    else:
        # Crear nuevo usuario
        db_user = User(
            email=user_data["email"],
            name=user_data.get("name", ""),
            profile_image=user_data.get("profile_image"),
            password_hash="",  # No se necesita contraseña para usuarios OAuth
            email_verified=True,  # Los correos de proveedores OAuth ya están verificados
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    # Si se proporcionaron datos del token, almacenarlos
    if token_data and "access_token" in token_data:
        create_oauth2_token(
            db=db,
            user_id=db_user.id,
            provider=user_data.get("provider", "google"),
            token_data=token_data
        )
    
    return db_user