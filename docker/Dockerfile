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

# Instalar dependencias con versiones específicas para evitar conflictos
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pydantic==1.10.7 python-dateutil==2.8.2 asgiref==3.7.2 mysqlclient

# Copiar el código de la aplicación
COPY backend /app/

# Variables de entorno
ENV PYTHONPATH=/app \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para iniciar la aplicación con uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
