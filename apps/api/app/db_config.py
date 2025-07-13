import os
import sys

# Debug helper to print to stderr where it will always be visible
def debug_print(message):
    print(message, file=sys.stderr, flush=True)

# Function to check if an environment variable exists and return its value
def get_required_env(name):
    value = os.getenv(name)
    if value is None:
        print(f"\n{'='*50}")
        print(f"ERROR: Required environment variable '{name}' is not set")
        print(f"Please ensure all required database variables are defined in the .env file")
        print(f"{'='*50}\n")
        sys.exit(1)
    return value

# Get required database environment variables
DB_HOST = get_required_env("DB_HOST")
DB_PORT = get_required_env("DB_PORT")
DB_NAME = get_required_env("DB_NAME")
DB_USER = get_required_env("DB_USER")
DB_PASSWORD = get_required_env("DB_PASSWORD")

# Construir la URL de conexión
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
debug_print(f"Configured database connection: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

# Función para obtener una URL alternativa (ej: para pruebas)
def get_database_url(environment=None):
    """
    Obtiene la URL de la base de datos según el ambiente
    """
    env = environment or os.getenv("ENVIRONMENT")
    
    if env == "test":
        # Para pruebas, usar una base de datos diferente
        return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/moneydiary_test"
    elif env == "production":
        # En producción, usar la URL exacta desde variables de entorno
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            debug_print("Warning: DATABASE_URL not set in production environment, using constructed URL")
        return db_url or DATABASE_URL
    else:
        # Para desarrollo, usar la URL construida
        return DATABASE_URL