from logging.config import fileConfig
import logging
import traceback
import sys
import os
import importlib

from sqlalchemy import engine_from_config
from sqlalchemy import pool, text, inspect
from sqlalchemy.engine.url import URL

from alembic import context

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('alembic')

# Get environment
ENV = os.environ.get("ENVIRONMENT", "development")
logger.info(f"Running in {ENV} environment")

# Import the Base class that contains the models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base model
from app.models.base import Base

# Import all individual model modules to ensure they're registered
import app.models.account_types
import app.models.accounts
import app.models.budget
import app.models.categories
import app.models.csv_imports
import app.models.envelopes
import app.models.financial_goals
import app.models.financial_methods
import app.models.invalidated_token
import app.models.oauth2_token
import app.models.permission
import app.models.projections
import app.models.recurring_patterns
import app.models.role
import app.models.simulations
import app.models.transactions
import app.models.users

# Verify models are loaded
for tablename, table in Base.metadata.tables.items():
    print(f"Table registered in metadata: {tablename}")

# Make metadata available for alembic
target_metadata = Base.metadata

# Configure database connection from environment variables
def get_db_url():
    """Get database URL from environment variables based on current environment."""
    # Use environment-specific database settings
    if ENV == "development":
        host = os.environ.get("DEV_DB_HOST", "localhost")
        port = os.environ.get("DEV_DB_PORT", "5432")
        name = os.environ.get("DEV_DB_NAME", "moneydiary_dev")
        user = os.environ.get("DEV_DB_USER", "postgres")
        password = os.environ.get("DEV_DB_PASS", "postgres")
    elif ENV == "testing":
        host = os.environ.get("TEST_DB_HOST", "localhost")
        port = os.environ.get("TEST_DB_PORT", "5432")
        name = os.environ.get("TEST_DB_NAME", "moneydiary_test")
        user = os.environ.get("TEST_DB_USER", "postgres")
        password = os.environ.get("TEST_DB_PASS", "postgres")
    elif ENV == "production":
        host = os.environ.get("PROD_DB_HOST", "localhost")
        port = os.environ.get("PROD_DB_PORT", "5432")
        name = os.environ.get("PROD_DB_NAME", "moneydiary")
        user = os.environ.get("PROD_DB_USER", "postgres")
        password = os.environ.get("PROD_DB_PASS", "postgres")
    else:
        # Default to development
        host = os.environ.get("DEV_DB_HOST", "localhost")
        port = os.environ.get("DEV_DB_PORT", "5432")
        name = os.environ.get("DEV_DB_NAME", "moneydiary_dev")
        user = os.environ.get("DEV_DB_USER", "postgres")
        password = os.environ.get("DEV_DB_PASS", "postgres")

    # Construct and return connection URL
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"

def include_name_in_schema(name, type_, parent_names):
    """Filter function for Alembic to decide which schema names to include."""
    if type_ == "schema":
        return name in ("app", "audit")  # Only include app and audit schemas
    return True

def include_object(object, name, type_, reflected, compare_to):
    """
    Filter function for Alembic to decide which database objects to include in migrations.
    
    Args:
        object: The SQLAlchemy object being considered
        name: The name of the object
        type_: The type of the object (table, column, etc.)
        reflected: Whether the object was reflected (loaded from db) or not
        compare_to: The object being compared to, if any
        
    Returns:
        bool: True if the object should be included in migrations, False otherwise
    """
    # Only include objects in the 'app' or 'audit' schema
    if type_ == "table" and hasattr(object, "schema"):
        if object.schema not in ("app", "audit", None):
            return False
            
    # Exclude system tables like alembic_version unless they're in our schema
    if name == "alembic_version":
        if hasattr(object, "schema") and object.schema != "app":
            return False
    
    # Include all other objects
    return True

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

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    # Get database URL from environment
    url = get_db_url()
    logger.info(f"Using database URL: {url} (offline mode)")
    
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
        include_object=include_object,
        include_name=include_name_in_schema,  # Add the name filter function
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Get the database URL
    db_url = get_db_url()
    logger.info(f"Using database URL: {db_url}")
    
    # Create configuration for the database engine
    config = context.config
    config.set_main_option("sqlalchemy.url", db_url)
    
    # Create the engine with our configuration
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        isolation_level="AUTOCOMMIT",
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
            
            # Perform database inspection if needed
            try:
                inspect_database(connection)
            except Exception as inspect_error:
                logger.error(f"Error during database inspection: {str(inspect_error)}")
            
            # Configure the migration context simply
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                include_name=include_name_in_schema,  # Add the name filter function
                version_table="alembic_version",
                version_table_schema="app",
                schema_translate_map={None: "app", "app": "app"},
                # Opciones adicionales para forzar comparación detallada
                compare_type=True,
                compare_server_default=True,
                include_symbol=True,  # Incluir todos los objetos
                render_as_batch=True  # Usar modo batch más detallado
            )
            
            logger.info("Alembic context configured successfully")
            
            # Run migrations with transaction handling by Alembic
            with context.begin_transaction():
                context.run_migrations()
                logger.info("Migrations completed successfully")
            
            # Verify the results
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
            raise

# Debug: print detected tables in SQLAlchemy models
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

# Call the appropriate function based on context configuration
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
