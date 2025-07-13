  #!/usr/bin/env python
"""
Script para crear usuarios administradores en MoneyDiary
Uso: python scripts/create_admin.py --email admin@example.com --name "Nombre Admin" --password "contraseña_segura"
"""

import argparse
import os
import sys
import bcrypt
from datetime import datetime, timezone

# Añadir el directorio raíz del proyecto al path para poder importar las dependencias
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.users import User
from app.models.role import Role

def create_admin_user(email, name, password, verify_password=True):
    """
    Crea un usuario con rol de administrador en la base de datos.
    
    Args:
        email: Email del administrador
        name: Nombre completo del administrador
        password: Contraseña del administrador
        verify_password: Si es True, solicita confirmación de contraseña
    
    Returns:
        bool: True si se creó con éxito, False en caso contrario
    """
    # Verificar que la contraseña sea segura (mínimo 12 caracteres)
    if len(password) < 12:
        print("Error: La contraseña debe tener al menos 12 caracteres")
        return False
    
    # Verificación de contraseña
    if verify_password:
        confirm_password = input("Confirma la contraseña: ")
        if password != confirm_password:
            print("Error: Las contraseñas no coinciden")
            return False
    
    # Iniciar sesión de base de datos
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un usuario con ese email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Error: Ya existe un usuario con el email {email}")
            return False
        
        # Buscar el rol de administrador
        admin_role = db.query(Role).filter(Role.name == 'admin').first()
        if not admin_role:
            print("Error: No se encontró el rol de administrador. "
                  "Asegúrate de haber ejecutado las migraciones que crean los roles.")
            return False
        
        # Generar hash de la contraseña con bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear el nuevo usuario administrador
        new_admin = User(
            name=name,
            email=email,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
            role_id=admin_role.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Guardar en la base de datos
        db.add(new_admin)
        db.commit()
        
        print(f"✅ Usuario administrador '{name}' ({email}) creado exitosamente")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear el usuario administrador: {str(e)}")
        return False
        
    finally:
        db.close()

def main():
    """Función principal que procesa los argumentos de la línea de comandos"""
    parser = argparse.ArgumentParser(description='Crear un usuario administrador para MoneyDiary')
    
    parser.add_argument('--email', required=True, help='Email del administrador')
    parser.add_argument('--name', required=True, help='Nombre completo del administrador')
    parser.add_argument('--password', help='Contraseña del administrador (si no se proporciona, se solicitará)')
    parser.add_argument('--non-interactive', action='store_true', 
                      help='Modo no interactivo (no pide confirmación)')
    
    args = parser.parse_args()
    
    # Si no se proporcionó contraseña, solicitarla de forma segura
    password = args.password
    if not password:
        import getpass
        password = getpass.getpass("Ingresa la contraseña para el administrador: ")
    
    # Crear el usuario administrador
    create_admin_user(args.email, args.name, password, not args.non_interactive)

if __name__ == '__main__':
    main()