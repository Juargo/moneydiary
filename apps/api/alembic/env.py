from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, text

from alembic import context

# importar la clase Base que contiene los modelos
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar todos los modelos de una vez
from app.models import Base
from app.models import *
from app.config import settings

# Determinar el ambiente actual
ENV = os.environ.get("APP_ENV", "development")
print(f"Running migrations in {ENV} environment")

# Obtener credenciales desde variables de entorno según el ambiente
def get_db_url_from_env(env):
    if env == "development":
        db_host = os.environ.get("DEV_DB_HOST", "localhost")
        db_port = os.environ.get("DEV_DB_PORT", "5432")
        db_name = os.environ.get("DEV_DB_NAME", "moneydiary_dev")
        db_user = os.environ.get("DEV_DB_USER", "postgres")
        db_pass = os.environ.get("DEV_DB_PASS", "postgres")
    elif env == "testing":
        db_host = os.environ.get("TEST_DB_HOST", "localhost")
        db_port = os.environ.get("TEST_DB_PORT", "5432")
        db_name = os.environ.get("TEST_DB_NAME", "moneydiary_test")
        db_user = os.environ.get("TEST_DB_USER", "postgres")
        db_pass = os.environ.get("TEST_DB_PASS", "postgres")
    elif env == "production":
        db_host = os.environ.get("PROD_DB_HOST", "localhost")
        db_port = os.environ.get("PROD_DB_PORT", "5432")
        db_name = os.environ.get("PROD_DB_NAME", "moneydiary")
        db_user = os.environ.get("PROD_DB_USER", "postgres")
        db_pass = os.environ.get("PROD_DB_PASS", "postgres")
    else:
        raise ValueError(f"Unknown environment: {env}")
    
    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# este es el objeto Alembic Config que provee
# acceso a los valores dentro del archivo .ini
config = context.config

# Sobreescribir la URL de la base de datos según el ambiente
db_url = get_db_url_from_env(ENV)
config.set_main_option("sqlalchemy.url", db_url)

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

    # Función para filtrar qué objetos incluir en la migración
    def include_object(object, name, type_, reflected, compare_to):
        # Solo incluir objetos en el schema 'app' o 'audit'
        if type_ == "table" and object.schema not in ("app", "audit", None):
            return False
        # Excluir tablas del sistema
        if name == "alembic_version" and object.schema != "app":
            return False
        return True

    with connectable.connect() as connection:
        # Establecer search_path antes de la configuración
        connection.execute(text("SET search_path TO app, public"))
        
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Configuración para el manejo de schemas
            include_schemas=True,
            include_object=include_object,
            version_table="alembic_version",
            version_table_schema="app",
            # Crear la tabla alembic_version en el schema app
            schema_translate_map={"schema": "app"}
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
