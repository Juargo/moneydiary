import asyncio
import os
import sys
import socket
from datetime import datetime
from tortoise import Tortoise, connections

from app.db.config import TORTOISE_ORM, DATABASE_URL

async def check_connection():
    """Verifica la conexión a la base de datos."""
    print(f"[{datetime.now().isoformat()}] Verificando conexión a la base de datos...")
    print(f"Cadena de conexión: {DATABASE_URL}")
    
    # Variables de entorno
    host = os.getenv('MYSQL_HOST')
    port = os.getenv('MYSQL_PORT')
    db = os.getenv('MYSQL_DB')
    user = os.getenv('MYSQL_USER')
    
    print(f"Host configurado: {host}")
    print(f"Puerto configurado: {port}")
    print(f"Base de datos: {db}")
    print(f"Usuario: {user}")
    
    # Comprobar resolución DNS
    try:
        print(f"Resolviendo DNS para {host}...")
        ip_address = socket.gethostbyname(host)
        print(f"Dirección IP de {host}: {ip_address}")
    except socket.gaierror:
        print(f"❌ No se pudo resolver el nombre de host: {host}")
    
    # Comprobar si el puerto está abierto
    try:
        print(f"Comprobando si el puerto {port} está abierto en {host}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, int(port)))
        if result == 0:
            print(f"✅ El puerto {port} está abierto en {host}")
        else:
            print(f"❌ El puerto {port} está cerrado o bloqueado en {host}")
        sock.close()
    except Exception as e:
        print(f"❌ Error al comprobar el puerto: {str(e)}")
    
    try:
        # Inicializar Tortoise ORM
        await Tortoise.init(config=TORTOISE_ORM)
        
        # Verificar la conexión
        conn = connections.get("default")
        result = await conn.execute_query("SELECT 1")
        
        print("✅ Conexión exitosa a la base de datos MySQL")
        print(f"Resultado de la consulta: {result}")
        return True
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {str(e)}")
        return False
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    success = asyncio.run(check_connection())
    sys.exit(0 if success else 1)
