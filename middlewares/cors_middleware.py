"""
Middleware de CORS para o sistema EmployeeVirtual
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurações de CORS
def get_cors_origins():
    """
    Obtém as origens permitidas do arquivo .env
    
    Returns:
        Lista de origens permitidas ou lista vazia se não configurado
    """
    origins = os.getenv('CORS_ORIGINS')
    if origins:
        return [origin.strip() for origin in origins.split(',')]
    return []

def add_cors_middleware(app: FastAPI):
    """
    Adiciona middleware de CORS à aplicação
    
    Args:
        app: Instância do FastAPI
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

