from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# importar la clase Base que contiene los modelos
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.base import Base
from app.config import settings

# este es el objeto Alembic Config que provee
# acceso a los valores dentro del archivo .ini
config = context.config

# sobreescribir la url de conexión con la de las variables de entorno
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpretar el archivo de configuración para Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# agregar aquí todos los modelos que quieres incluir en las migraciones
target_metadata = Base.metadata

def run_migrations_offline():
    """Ejecutar migraciones en modo 'offline'.

    Esto configura el contexto de migración con solo una URL
    y no un engine, aunque en nuestra experiencia siempre
    usarás un engine.

    Llamando a esto con el contexto configurado con una URL
    disponible se ejecutan migraciones en 'modo offline'.
    Esto solo crea el script SQL.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Ejecutar migraciones en modo 'online'.

    En este escenario creamos un Engine y lo asociamos con el
    contexto de la migración.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # usar schema 'app' para todas las tablas
            include_schemas=True,
            version_table_schema="app"
        )

        with context.begin_transaction():
            # Registro de la versión actual de la aplicación
            context.execute(f"SET search_path TO app, public")
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
