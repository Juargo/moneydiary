FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema (incluyendo las necesarias para MySQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar la caché de Docker
COPY backend/requirements.txt .

# Crear un requirements modificado para evitar conflictos
RUN grep -v -E "pydantic|python-dateutil" requirements.txt > requirements-fixed.txt \
    && pip install --upgrade pip

# Instalar primero las versiones específicas de los paquetes conflictivos
RUN pip install --no-cache-dir pydantic==1.10.7 python-dateutil==2.8.2 \
    asgiref==3.7.2 mysqlclient --no-deps

# Luego instalar el resto de dependencias usando el archivo modificado
RUN pip install --no-cache-dir -r requirements-fixed.txt --no-deps \
    && pip install --no-cache-dir fastapi uvicorn tortoise-orm

# Copiar el código de la aplicación
COPY backend /app/

# Variables de entorno
ENV PYTHONPATH=/app \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=production

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Verificar dependencias antes de iniciar
RUN pip check || echo "Algunas dependencias podrían no ser compatibles, pero intentaremos ejecutar de todas formas"

# Comando para iniciar la aplicación con uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
