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

# def create_user_oauth(db: Session, user_data: dict) -> User:
#     """
#     Crea o actualiza un usuario a partir de datos de OAuth
    
#     Args:
#         db: Sesión de base de datos
#         user_data: Datos del usuario devueltos por el proveedor OAuth
        
#     Returns:
#         User: Usuario creado o actualizado
#     """
#     try:
#         print(f"Procesando usuario OAuth con email: {user_data.get('email', 'NO EMAIL')}")
        
#         # Verificar que el email existe
#         if not user_data.get('email'):
#             raise ValueError("El email es requerido para crear un usuario")
            
#         # Buscar usuario existente por email
#         db_user = get_user_by_email(db, user_data["email"])
        
#         print(f"Usuario encontrado: {db_user.email if db_user else 'Ninguno'}")
#         # Si el usuario ya existe, actualizar sus datos
#         if db_user:
#             # Actualizar usuario existente
#             print(f"Actualizando usuario existente: ID={db_user.id}, Email={db_user.email}")
#             db_user.name = user_data.get("name", db_user.name)
#             db_user.profile_image = user_data.get("profile_image", db_user.profile_image)
#             # db_user.provider = user_data.get("provider", db_user.provider)
#             # db_user.provider_user_id = user_data.get("provider_user_id", db_user.provider_user_id)
#             db_user.is_active = True
#             db_user.last_login = datetime.now()
            
#             db.commit()
#             db.refresh(db_user)
#             print(f"Usuario actualizado: ID={db_user.id}, Email={db_user.email}")
#             return db_user
#         else:
#             # Crear nuevo usuario
#             print(f"Creando nuevo usuario: Email={user_data['email']}")

#             # Generar un hash seguro aleatorio para satisfacer la restricción NOT NULL
#             import secrets
#             import hashlib
#             # Genera un hash seguro para cumplir con la restricción de password_hash
#             random_password = secrets.token_hex(16)  # 32 caracteres aleatorios
#             password_hash = hashlib.sha256(random_password.encode()).hexdigest()

#             new_user = User(
#                 email=user_data["email"],
#                 name=user_data.get("name", ""),
#                 profile_image=user_data.get("profile_image", ""),
#                 # provider=user_data.get("provider", "google"),
#                 # provider_user_id=user_data.get("provider_user_id", ""),
#                 is_active=True,
#                 email_verified=user_data.get("email_verified", False),
#                 password_hash=password_hash, 
#                 last_login=datetime.now()
#             )
            
#             db.add(new_user)
#             db.commit()
#             db.refresh(new_user)
#             print(f"Nuevo usuario creado: ID={new_user.id}, Email={new_user.email}")
#             return new_user
#     except Exception as e:
#         db.rollback()
#         print(f"Error al crear/actualizar usuario OAuth: {str(e)}")
#         raise