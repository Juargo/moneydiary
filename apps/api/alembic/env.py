from logging.config import fileConfig
import logging
import traceback
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool, text, inspect

from alembic import context

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('alembic')

# Import the Base class that contains the models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models at once
from app.models import Base
from app.models import *
from app.config import settings

# Set up more detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar de INFO a DEBUG
    format='%(levelname)s [%(name)s] %(message)s'
)
logger = logging.getLogger('alembic')
# También configurar el logging para SQLAlchemy
logging.getLogger('sqlalchemy').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Determine the current environment
ENV = os.environ.get("ENVIRONMENT", os.environ.get("APP_ENV", "development"))
print(f"Running migrations in {ENV} environment")
print(f"Configured database connection: ", end="")

# Get credentials from environment variables based on environment
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
    
    # Log the connection details (without password)
    print(f"{db_host}:{db_port}/{db_name} as {db_user}")
    
    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# This is the Alembic Config object, which provides
# access to the values within the .ini file
config = context.config

# Overwrite the database URL based on the environment
db_url = get_db_url_from_env(ENV)
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add all models you want to include in migrations here
target_metadata = Base.metadata

# Function to filter which objects to include in the migration
def include_object(object, name, type_, reflected, compare_to):
    # Only include objects in the 'app' or 'audit' schema
    if type_ == "table" and object.schema not in ("app", "audit", None):
        return False
    # Exclude system tables
    if name == "alembic_version" and object.schema != "app":
        return False
    return True

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table="alembic_version",
        version_table_schema="app",
        schema_translate_map={None: "app", "app": "app"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Configure engine with specific options for better PostgreSQL handling
    config_section = config.get_section(config.config_ini_section)
    
    # Create a connection with autocommit mode
    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        isolation_level="AUTOCOMMIT",  # Use AUTOCOMMIT isolation level
        connect_args={
            "options": "-c timezone=utc -c search_path=app,public"
        },
    )
    
    # Prepare database with a separate connection - explicitly create schema
    with connectable.connect() as conn:
        try:
            logger.info(f"Preparing database with dedicated connection: {conn.engine.url}")
            
            # Simple schema setup - just create schema and set search_path
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
            logger.info("Created schema 'app' if it didn't exist")
            
            conn.execute(text("SET search_path TO app, public"))
            logger.info("Set search_path to app, public")
            
            # Obtener nombre de la base de datos según el entorno actual
            if ENV == "development":
                db_name = os.environ.get("DEV_DB_NAME", "moneydiary_dev")
            elif ENV == "testing":
                db_name = os.environ.get("TEST_DB_NAME", "moneydiary_test")
            elif ENV == "production":
                db_name = os.environ.get("PROD_DB_NAME", "moneydiary")
            else:
                db_name = "moneydiary_dev"  # fallback
            
            # Set search_path at database level so it persists (using dynamic db_name)
            conn.execute(text(f"ALTER DATABASE {db_name} SET search_path TO app, public"))
            logger.info(f"Set database-level search_path for database {db_name}")
            
            # Verify schema creation
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'app'"))
            if result.scalar():
                logger.info("Schema 'app' exists and is accessible")
            else:
                logger.error("Schema 'app' doesn't exist despite creation attempt")
                raise Exception("Failed to create schema 'app'")
                
        except Exception as schema_error:
            logger.error(f"Error preparing database: {str(schema_error)}")
            logger.error(traceback.format_exc())
            raise

    # Now proceed with migration connection
    with connectable.connect() as connection:
        try:
            # Log connection information (only once)
            logger.info(f"Connected to database for migrations: {connection.engine.url}")
            
            # Make sure search_path is set for this connection too
            connection.execute(text("SET search_path TO app, public"))
            logger.info("Search path set for migration connection")
            
            # Configure the migration context simply
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                version_table="alembic_version",
                version_table_schema="app",
                schema_translate_map={None: "app", "app": "app"},
                compare_type=True,
                compare_server_default=True,
                # Agregar estas opciones para debugging:
                template_args={"opts": {"compare_type": True, "compare_server_default": True}},
                render_as_batch=True,
                include_name=True,
                include_symbol=True
            )
            
            logger.info("Alembic context configured successfully")
            
            # Run migrations with transaction handling by Alembic
            with context.begin_transaction():
                context.run_migrations()
                logger.info("Migrations completed successfully")
            try:
                # Execute direct SQL to list tables in app schema
                result = connection.execute(text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'app' ORDER BY tablename"
                ))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"Tables in app schema after migration: {tables}")
                
                # Check each table individually for debugging
                for table_name in tables:
                    try:
                        # Count rows in each table to verify it exists
                        result = connection.execute(text(f"SELECT COUNT(*) FROM app.{table_name}"))
                        count = result.scalar()
                        logger.info(f"Table app.{table_name} has {count} rows")
                    except Exception as table_err:
                        logger.error(f"Error checking table app.{table_name}: {str(table_err)}")
            except Exception as verify_error:
                # Just log verification errors, don't fail the migration
                logger.error(f"Error verifying tables: {str(verify_error)}")
                
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            # Simple schema setup - just create schema and set search_path
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
            logger.info("Created schema 'app' if it didn't exist")
            
            conn.execute(text("SET search_path TO app, public"))
            logger.info("Set search_path to app, public")
            
            # Obtener nombre de la base de datos según el entorno actual
            if ENV == "development":
                db_name = os.environ.get("DEV_DB_NAME", "moneydiary_dev")
            elif ENV == "testing":
                db_name = os.environ.get("TEST_DB_NAME", "moneydiary_test")
            elif ENV == "production":
                db_name = os.environ.get("PROD_DB_NAME", "moneydiary")
            else:
                db_name = "moneydiary_dev"  # fallback
            
            # Set search_path at database level so it persists (using dynamic db_name)
            conn.execute(text(f"ALTER DATABASE {db_name} SET search_path TO app, public"))
            logger.info(f"Set database-level search_path for database {db_name}")
            
def inspect_database(connection):
    """Inspecciona la base de datos para comparar con los modelos."""
    logger.info("=== ESTRUCTURA ACTUAL DE LA BASE DE DATOS ===")
    inspector = inspect(connection)
    
    # Verificar schemas
    schemas = inspector.get_schema_names()
    logger.info(f"Schemas en la base de datos: {schemas}")
    
    # Verificar tablas en cada schema
    for schema in schemas:
        tables = inspector.get_table_names(schema=schema)
        logger.info(f"Tablas en schema '{schema}': {tables}")
        
        for table in tables:
            logger.info(f"Detalles de tabla '{schema}.{table}':")
            # Columnas
            columns = inspector.get_columns(table, schema=schema)
            for column in columns:
                logger.info(f"  - Columna: {column['name']}, Tipo: {column['type']}")
            
            # Primary keys
            pks = inspector.get_pk_constraint(table, schema=schema)
            logger.info(f"  - Primary keys: {pks['constrained_columns']}")
            
            # Foreign keys
            fks = inspector.get_foreign_keys(table, schema=schema)
            for fk in fks:
                logger.info(f"  - FK: {fk['constrained_columns']} -> {fk['referred_schema']}.{fk['referred_table']}.{fk['referred_columns']}")
    
    logger.info("=====================")

# En run_migrations_online, agregar esta llamada después de conectar pero antes de configurar el contexto
# Ensure connectable is defined before this block
connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
    isolation_level="AUTOCOMMIT",
    connect_args={"options": "-c timezone=utc -c search_path=app,public"},
)

with connectable.connect() as connection:
    try:
        # Log connection information
        logger.info(f"Connected to database for inspection: {connection.engine.url}")
        inspect_database(connection)
        
        # El resto del código...
    except Exception as e:
        logger.error(f"Error during database inspection: {str(e)}")

# Depuración de modelos SQLAlchemy
logger.info("=== MODELOS CARGADOS ===")
model_count = 0
for table_name, table in Base.metadata.tables.items():
    model_count += 1
    logger.info(f"Modelo: {table_name} (Schema: {table.schema})")
    # Listar las columnas
    for column in table.columns:
        logger.info(f"  - Columna: {column.name}, Tipo: {column.type}, Nullable: {column.nullable}")
    # Listar las foreign keys
    for fk in table.foreign_keys:
        logger.info(f"  - FK: {fk.column} -> {fk.target_fullname}")

logger.info(f"Total de modelos cargados: {model_count}")
logger.info("=====================")
