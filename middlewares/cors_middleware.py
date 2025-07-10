"""
Middleware de CORS para o sistema EmployeeVirtual
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app: FastAPI):
    """
    Adiciona middleware de CORS à aplicação
    
    Args:
        app: Instância do FastAPI
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar domínios
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

