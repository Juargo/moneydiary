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
ENV = os.environ.get("ALEMBIC_ENVIRONMENT")
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
import app.models.file_imports
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
import app.models.banks

# Verify models are loaded
for tablename, table in Base.metadata.tables.items():
    print(f"Table registered in Base.metadata.tables: {tablename}")

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
    """Filter function for deciding which database objects to include."""
    # Add debug logging
    logger.debug(f"Checking object: {name}, type: {type_}, schema: {getattr(object, 'schema', None)}")
    
    # Only include objects in the 'app' or 'audit' schema
    if type_ == "table" and hasattr(object, "schema"):
        if object.schema not in ("app", "audit", None):
            logger.debug(f"Excluding {name} because schema is {object.schema}")
            return False
            
    # Exclude system tables like alembic_version unless they're in our schema
    if name == "alembic_version":
        if hasattr(object, "schema") and object.schema != "app":
            logger.debug(f"Excluding alembic_version in schema {getattr(object, 'schema', None)}")
            return False
    
    # Include all other objects
    return True

def inspect_database(connection):
    """Inspecciona la base de datos para comparar con los modelos."""
    logger.info("\n=== ESTRUCTURA ACTUAL DE LA BASE DE DATOS ===\n")
    inspector = inspect(connection)
    
    # Verificar schemas
    schemas = inspector.get_schema_names()
    logger.info(f"Schemas en la base de datos: {schemas}\n")
    
    # Verificar tablas en cada schema
    for schema in schemas:
        tables = inspector.get_table_names(schema=schema)
        logger.info(f"Tablas en schema '{schema}': {tables}\n")
        
        for table in tables:
            logger.info(f"Detalles de tabla '{schema}.{table}':\n")
            # Columnas
            columns = inspector.get_columns(table, schema=schema)
            for column in columns:
                logger.info(f"  - Columna: {column['name']}, Tipo: {column['type']}\n")
            
            # Primary keys
            pks = inspector.get_pk_constraint(table, schema=schema)
            logger.info(f"  - Primary keys: {pks['constrained_columns']}\n")
            
            # Foreign keys
            fks = inspector.get_foreign_keys(table, schema=schema)
            for fk in fks:
                logger.info(f"  - FK: {fk['constrained_columns']} -> {fk['referred_schema']}.{fk['referred_table']}.{fk['referred_columns']}\n")
    
    logger.info("\n=====================\n")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    # Get database URL from environment
    url = get_db_url()
    logger.info(f"\nUsing database URL: {url} (offline mode)\n")
    
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
    logger.info(f"\nUsing database URL: {db_url}\n")
    
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
            logger.info(f"\nPreparing database with dedicated connection: {conn.engine.url}\n")
            
            # Simple schema setup - just create schema and set search_path
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
            logger.info("Created schema 'app' if it didn't exist\n")
            
            conn.execute(text("SET search_path TO app, public"))
            logger.info("Set search_path to app, public\n")
            db_name = os.environ.get("ALEMBIC_DB_NAME")
            
            # Set search_path at database level so it persists (using dynamic db_name)
            conn.execute(text(f"ALTER DATABASE {db_name} SET search_path TO app, public"))
            logger.info(f"Set database-level search_path for database {db_name}\n")
            
            # Verify schema creation
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'app'"))
            if result.scalar():
                logger.info("Schema 'app' exists and is accessible\n")
            else:
                logger.error("\nSchema 'app' doesn't exist despite creation attempt\n")
                raise Exception("Failed to create schema 'app'")
                
        except Exception as schema_error:
            logger.error(f"\nError preparing database: {str(schema_error)}\n")
            logger.error(traceback.format_exc())
            raise

    # Now proceed with migration connection
    with connectable.connect() as connection:
        try:
            # Log connection information (only once)
            logger.info(f"\nConnected to database for migrations: {connection.engine.url}\n")
            
            # Make sure search_path is set for this connection too
            connection.execute(text("SET search_path TO app, public"))
            logger.info("Search path set for migration connection\n")
            
            # Perform database inspection if needed
            try:
                inspect_database(connection)
            except Exception as inspect_error:
                logger.error(f"\nError during database inspection: {str(inspect_error)}\n")
            
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
            
            logger.info("Alembic context configured successfully\n")
            
            # Run migrations with transaction handling by Alembic
            with context.begin_transaction():
                context.run_migrations()
                logger.info("Migrations completed successfully\n")
            
            # Verify the results
            try:
                # Execute direct SQL to list tables in app schema
                result = connection.execute(text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'app' ORDER BY tablename"
                ))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"\nTables in app schema after migration: {tables}\n")
                
                # Check each table individually for debugging
                for table_name in tables:
                    try:
                        # Count rows in each table to verify it exists
                        result = connection.execute(text(f"SELECT COUNT(*) FROM app.{table_name}"))
                        count = result.scalar()
                        logger.info(f"Table app.{table_name} has {count} rows")
                    except Exception as table_err:
                        logger.error(f"\nError checking table app.{table_name}: {str(table_err)}\n")
            except Exception as verify_error:
                # Just log verification errors, don't fail the migration
                logger.error(f"\nError verifying tables: {str(verify_error)}\n")
                
        except Exception as e:
            logger.error(f"\nError during migration: {str(e)}\n")
            raise

# Debug: print detected tables in SQLAlchemy models
logger.info("\n=== MODELOS SCRIPTS SCHEMA CARGADOS ===\n")
model_count = 0
for table_name, table in Base.metadata.tables.items():
    model_count += 1
    logger.info(f"\nModelo: {table_name} (Schema: {table.schema})")
    # Listar las columnas
    for column in table.columns:
        logger.info(f"  - Columna: {column.name}, Tipo: {column.type}, Nullable: {column.nullable}")
    # Listar las foreign keys
    for fk in table.foreign_keys:
        logger.info(f"  - FK: {fk.column} -> {fk.target_fullname}")

logger.info(f"\nTotal de modelos cargados: {model_count}\n")
logger.info("\n=====================\n")

# Call the appropriate function based on context configuration
logger.info("\n=== INICIANDO MIGRACIONES ===\n")
# Check if running in offline mode
if context.is_offline_mode():
    logger.info("Running in offline mode\n")
else:
    logger.info("Running in online mode\n")
# Run migrations based on the context mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
