"""
Aplicação principal do sistema EmployeeVirtual
"""
from fastapi import FastAPI

# Apenas CORS middleware - o que importa
from middlewares.cors_middleware import add_cors_middleware

# Import do configurador de routers - uma linha só
from api.router_config import register_routers

# Criar aplicação FastAPI
app = FastAPI(
    title="EmployeeVirtual API",
    description="API completa para o sistema EmployeeVirtual - Agentes de IA, Automações e Chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adicionar apenas CORS middleware - como sempre funcionou
add_cors_middleware(app)

# Registrar todos os routers automaticamente - uma linha só
register_routers(app)

@app.get("/")
async def root():
    """
    Endpoint raiz da API
    
    Returns:
        Informações básicas da API
    """
    return {
        "message": "EmployeeVirtual API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint de health check - SIMPLES sem banco
    
    Returns:
        Status básico da aplicação
    """
    return {
        "status": "healthy",
        "message": "EmployeeVirtual API is running",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    """
    Informações da API
    
    Returns:
        Informações detalhadas da API
    """
    return {
        "name": "EmployeeVirtual API",
        "version": "1.0.0",
        "description": "API completa para o sistema EmployeeVirtual",
        "status": "running"
    }

