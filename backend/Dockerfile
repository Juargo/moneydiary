FROM python:3.9-slim

WORKDIR /app

# Copiar requirements primero para aprovechar la caché
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY backend/app ./api

# Configurar variables de entorno
ENV PYTHONPATH=/app
ENV PORT=8000

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
