from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from .config import settings

protocol_logger = logging.getLogger("moneydiary.api.protocols")

async def protocol_metrics_middleware(request: Request, call_next):
    """
    Middleware para monitorear y registrar métricas de rendimiento
    específicas para cada protocolo API (REST vs GraphQL)
    """
    start_time = time.time()
    
    # Identificar el protocolo
    if request.url.path.startswith("/api/v1"):
        protocol = "REST"
    elif request.url.path.startswith("/graphql"):
        protocol = "GraphQL"
    else:
        protocol = "Other"
    
    # Procesar la solicitud
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time
    
    # Registrar métricas
    protocol_logger.info(
        f"Protocol: {protocol} | "
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.4f}s"
    )
    
    return response

def setup_middleware(app: FastAPI):
    """Configure all middleware for the application"""
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    app.middleware("http")(protocol_metrics_middleware)
