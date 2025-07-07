from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime
import traceback
from sqlalchemy import text
from typing import Dict, Any
from sqlalchemy.dialects import postgresql

from ..models.users import User
from ..models.oauth2_token import OAuth2Token

def get_user_by_email(db: Session, email: str) -> User:
    """
    Busca un usuario por su correo electrónico con depuración extendida
    """
    try:
        print(f"Buscando usuario por email: {email}")
        
        # Construir la query pero no ejecutarla aún
        query = db.query(User).filter(User.email == email)
        
        # Obtener la consulta SQL real que ejecutará SQLAlchemy
        sql = str(query.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        ))
        
        print(f"SQL generado: {sql}")
        
        # Ejecutar directamente con SQL nativo para verificar
        raw_result = db.execute(text(f"SELECT * FROM users WHERE email = :email"), {"email": email})
        result_count = raw_result.rowcount
        print(f"Consulta SQL nativa - Filas encontradas: {result_count}")
        
        # Ejecutar la consulta original
        result = query.first()
        print(f"Resultado: {result}")
        
        return result
        
    except Exception as e:
        print(f"ERROR en get_user_by_email: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Detalles del error: {traceback.format_exc()}")
        
        # Verificar si la tabla existe
        try:
            tables = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).fetchall()
            print(f"Tablas disponibles: {[t[0] for t in tables]}")
        except Exception as table_error:
            print(f"Error al verificar tablas: {str(table_error)}")
        
        # Verificar estructura de la tabla users si existe
        try:
            columns = db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'")).fetchall()
            print(f"Estructura de tabla users: {columns}")
        except Exception as col_error:
            print(f"Error al verificar columnas: {str(col_error)}")
            
        # Re-lanzar la excepción para mantener el comportamiento original
        raise

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
