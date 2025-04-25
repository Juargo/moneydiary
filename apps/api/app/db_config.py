import os
import sys

# Debug helper to print to stderr where it will always be visible
def debug_print(message):
    print(message, file=sys.stderr, flush=True)

# Obtener variables de entorno o usar valores predeterminados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")  # Puerto estándar de PostgreSQL
DB_NAME = os.getenv("DB_NAME", "moneydiary")
DB_USER = os.getenv("DB_USER", "moneydiary_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "moneydiary_password")

# Construir la URL de conexión
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
debug_print(f"Configured database connection: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

# Función para obtener una URL alternativa (ej: para pruebas)
def get_database_url(environment=None):
    """
    Obtiene la URL de la base de datos según el ambiente
    """
    env = environment or os.getenv("ENVIRONMENT", "development")
    
    if env == "test":
        # Para pruebas, usar una base de datos diferente
        return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/moneydiary_test"
    elif env == "production":
        # En producción, usar la URL exacta desde variables de entorno
        return os.getenv("DATABASE_URL", DATABASE_URL)
    else:
        # Para desarrollo, usar la URL por defecto
        return DATABASE_URL