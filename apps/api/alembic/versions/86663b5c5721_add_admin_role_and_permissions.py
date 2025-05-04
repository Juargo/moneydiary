"""add admin role and permissions

Revision ID: 86663b5c5721
Revises: 2bf73624c130
Create Date: 2025-05-04 00:15:54.672082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, text
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision: str = '86663b5c5721'
down_revision: Union[str, None] = '2bf73624c130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Crear tablas de referencia en memoria para insertar datos
    roles_table = table('roles',
        column('id', sa.Integer),
        column('name', sa.String),
        column('description', sa.String),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )
    
    permissions_table = table('permissions',
        column('id', sa.Integer),
        column('name', sa.String),
        column('description', sa.String),
        column('resource', sa.String),  # Campo obligatorio añadido
        column('action', sa.String),    # Campo obligatorio añadido
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )
    
    roles_permissions_table = table('roles_permissions',
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )
    
    # Insertar el rol de administrador
    op.bulk_insert(roles_table, [
        {
            'name': 'admin',
            'description': 'Administrador del sistema con acceso completo',
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
    ])
    
    # Insertar los permisos necesarios para la administración
    op.bulk_insert(permissions_table, [
        {
            'name': 'manage_banks',
            'description': 'Permite administrar bancos en el sistema',
            'resource': 'banks',      # Campo obligatorio
            'action': 'all',          # Campo obligatorio
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        },
        {
            'name': 'manage_users',
            'description': 'Permite administrar usuarios del sistema',
            'resource': 'users',      # Campo obligatorio
            'action': 'all',          # Campo obligatorio
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        },
        {
            'name': 'manage_roles',
            'description': 'Permite administrar roles y permisos',
            'resource': 'roles',      # Campo obligatorio
            'action': 'all',          # Campo obligatorio
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        },
        {
            'name': 'view_admin_dashboard',
            'description': 'Permite ver el panel de administración',
            'resource': 'dashboard',  # Campo obligatorio
            'action': 'read',         # Campo obligatorio
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
    ])
    
    # Ejecutar una consulta SQL para obtener los IDs
    # Obtenemos el ID del rol de administrador
    conn = op.get_bind()
    admin_role_id = conn.execute(text("SELECT id FROM roles WHERE name = 'admin'")).scalar()
    
    # Obtenemos los IDs de los permisos
    permission_ids = {}
    for permission_name in ['manage_banks', 'manage_users', 'manage_roles', 'view_admin_dashboard']:
        permission_ids[permission_name] = conn.execute(
            text(f"SELECT id FROM permissions WHERE name = '{permission_name}'")).scalar()
    
    # Asignar todos los permisos al rol de administrador
    for permission_name, permission_id in permission_ids.items():
        op.execute(
            roles_permissions_table.insert().values(
                role_id=admin_role_id,
                permission_id=permission_id
            )
        )

def downgrade():
    # Eliminar relaciones de permisos
    conn = op.get_bind()
    admin_role_id = conn.execute(text("SELECT id FROM roles WHERE name = 'admin'")).scalar()
    
    if admin_role_id:
        op.execute(text(f"DELETE FROM roles_permissions WHERE role_id = {admin_role_id}"))
    
    # Eliminar permisos
    for permission_name in ['manage_banks', 'manage_users', 'manage_roles', 'view_admin_dashboard']:
        op.execute(text(f"DELETE FROM permissions WHERE name = '{permission_name}'"))
    
    # Eliminar rol de administrador
    op.execute(text("DELETE FROM roles WHERE name = 'admin'"))