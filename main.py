"""
Aplicação principal do sistema EmployeeVirtual
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uvicorn
from contextlib import asynccontextmanager

# Imports dos módulos
from data.database import get_db, create_tables, get_connection_info
from data.mongodb import create_indexes, get_connection_info as get_mongo_info, close_mongo_connections
from middlewares.cors_middleware import add_cors_middleware
from middlewares.logging_middleware import LoggingMiddleware, RequestLoggingMiddleware
from middlewares.auth_middleware import RateLimitMiddleware

# Imports das APIs
from api.auth_api import router as auth_router
from api.agent_api import router as agent_router
from api.flow_api import router as flow_router
from api.chat_api import router as chat_router
from api.dashboard_api import router as dashboard_router
from api.file_api import router as file_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia ciclo de vida da aplicação
    
    Args:
        app: Instância do FastAPI
    """
    # Startup
    print("🚀 Iniciando EmployeeVirtual Backend...")
    
    # Verificar conexão com banco de dados (sem criar tabelas)
    try:
        # Apenas testa a conexão
        connection_info = get_connection_info()
        print(f"✅ Conexão com banco de dados verificada: {connection_info.get('database', 'N/A')}")
    except Exception as e:
        print(f"❌ Erro ao conectar com banco de dados: {e}")
        print("⚠️ Verifique suas configurações no arquivo .env")
        # Não continua se não conseguir conectar ao banco
        raise e
    
    # Criar índices do MongoDB (opcional)
    try:
        await create_indexes()
        print("✅ Índices do MongoDB criados/verificados")
    except Exception as e:
        print(f"⚠️ Aviso: MongoDB não disponível ou com erro (continuando mesmo assim): {e}")
    
    print("✅ EmployeeVirtual Backend iniciado com sucesso!")
    print("📚 Documentação disponível em: /docs")
    print("🏥 Health check disponível em: /health")
    
    yield
    
    # Shutdown
    print("🛑 Encerrando EmployeeVirtual Backend...")
    
    # Fechar conexões MongoDB
    try:
        close_mongo_connections()
        print("✅ Conexões fechadas")
    except Exception:
        pass

# Criar aplicação FastAPI
app = FastAPI(
    title="EmployeeVirtual API",
    description="API completa para o sistema EmployeeVirtual - Agentes de IA, Automações e Chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
    #lifespan=lifespan
)

# Adicionar middlewares
add_cors_middleware(app)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=1000, window_seconds=60)

# Registrar routers
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(agent_router, prefix="/api/agents", tags=["Agentes"])
app.include_router(flow_router, prefix="/api/flows", tags=["Flows/Automações"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat/Conversação"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard/Métricas"])
app.include_router(file_router, prefix="/api/files", tags=["Arquivos"])

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
async def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de health check
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Status da aplicação e dependências
    """
    try:
        # Verificar conexão SQL
        sql_info = get_connection_info()
        sql_status = "connected"
    except Exception as e:
        sql_info = {"error": str(e)}
        sql_status = "error"
    
    # Verificar conexão MongoDB
    mongo_info = get_mongo_info()
    mongo_status = "connected" if mongo_info.get("connected") else "error"
    
    # Status geral
    overall_status = "healthy" if sql_status == "connected" and mongo_status == "connected" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": "2024-01-01T00:00:00Z",  # Usar datetime real
        "services": {
            "sql_database": {
                "status": sql_status,
                "info": sql_info
            },
            "mongodb": {
                "status": mongo_status,
                "info": mongo_info
            }
        }
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
        "features": [
            "Autenticação JWT",
            "Agentes de IA personalizados",
            "Automações/Flows",
            "Chat/Conversação",
            "Dashboard e métricas",
            "Upload e processamento de arquivos",
            "Integração com Orion (serviços de IA)"
        ],
        "endpoints": {
            "auth": "/api/auth",
            "agents": "/api/agents",
            "flows": "/api/flows",
            "chat": "/api/chat",
            "dashboard": "/api/dashboard",
            "files": "/api/files"
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handler para exceções HTTP
    
    Args:
        request: Request HTTP
        exc: Exceção HTTP
        
    Returns:
        Response JSON com erro
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handler para exceções gerais
    
    Args:
        request: Request HTTP
        exc: Exceção
        
    Returns:
        Response JSON com erro
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erro interno do servidor",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )

# if __name__ == "__main__":
#     # Configurações do servidor
#     host = os.getenv("HOST", "0.0.0.0")
#     port = int(os.getenv("PORT", 8000))
#     debug = os.getenv("DEBUG", "false").lower() == "true"
    
#     print(f"🚀 Iniciando servidor em http://{host}:{port}")
#     print(f"📚 Documentação disponível em http://{host}:{port}/docs")
    
#     # Iniciar servidor
#     uvicorn.run(
#         "main:app",
#         host=host,
#         port=port,
#         reload=debug,
#         log_level="info"
#     )

