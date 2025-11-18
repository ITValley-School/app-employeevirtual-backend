"""
Middleware de CORS para o sistema EmployeeVirtual
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

# Configurações de CORS
def get_cors_origins():
    """
    Obtém as origens permitidas do arquivo .env
    
    Returns:
        Lista de origens permitidas ou lista padrão se não configurado
    """
    origins = os.getenv('CORS_ORIGINS')
    if origins:
        origins_list = [origin.strip() for origin in origins.split(',')]
        logger.info(f"CORS origins configuradas: {origins_list}")
        return origins_list
    
    # Fallback para origens padrão
    default_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ]
    logger.warning(f"CORS_ORIGINS não configurado no .env. Usando padrão: {default_origins}")
    return default_origins

def add_cors_middleware(app: FastAPI):
    """
    Adiciona middleware de CORS à aplicação
    
    Args:
        app: Instância do FastAPI
    """
    origins = get_cors_origins()
    
    # Garantir que ambas as variações de localhost/127.0.0.1 estão incluídas
    origins_set = set(origins)
    origins_set.add("http://localhost:5173")
    origins_set.add("http://127.0.0.1:5173")
    origins_set.add("http://localhost:3000")
    origins_set.add("http://127.0.0.1:3000")
    origins_set.add("http://localhost:8000")
    origins_set.add("http://127.0.0.1:8000")
    
    origins = list(origins_set)
    
    logger.info(f"Configurando CORS com origens: {origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
    
    logger.info(f"CORS middleware adicionado com {len(origins)} origem(ns)")


