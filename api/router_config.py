"""
Configuração centralizada de routers da API EmployeeVirtual
"""
from fastapi import FastAPI

# Imports dos routers
from api.auth_api import router as auth_router
from api.agent_api import router as agent_router
from api.flow_api import router as flow_router
from api.chat_api import router as chat_router
from api.dashboard_api import router as dashboard_router
from api.file_api import router as file_router
from api.metadata_api import router as metada_agent_router

# System Agents APIs
from api.system_agent_api import router as system_agent_router

# Configuração das rotas
ROUTER_CONFIG = [
    {
        "router": auth_router,
        "prefix": "/api/auth",
        "tags": ["Autenticação"]
    },
    {
        "router": agent_router,
        "prefix": "/api/agents", 
        "tags": ["Agentes"]
    },
    {
        "router": flow_router,
        "prefix": "/api/flows",
        "tags": ["Flows/Automações"]
    },
    {
        "router": chat_router,
        "prefix": "/api/chat",
        "tags": ["Chat/Conversação"]
    },
    {
        "router": dashboard_router,
        "prefix": "/api/dashboard",
        "tags": ["Dashboard/Métricas"]
    },
    {
        "router": file_router,
        "prefix": "/api/files",
        "tags": ["Arquivos"]
    },
    # System Agents APIs
    {
        "router": system_agent_router,
        "prefix": "/api",
        "tags": ["System Agents"]
    },
        # Metadata APIs
    {
        "router": metada_agent_router,
        "prefix": "/api",
        "tags": ["MetadadosAPI"]
    }
]


def register_routers(app: FastAPI) -> None:
    """
    Registra todos os routers na aplicação FastAPI
    
    Args:
        app: Instância do FastAPI onde os routers serão registrados
    """
    for config in ROUTER_CONFIG:
        app.include_router(
            config["router"],
            prefix=config["prefix"],
            tags=config["tags"]
        )
        print(f"✅ Router registrado: {config['prefix']} ({', '.join(config['tags'])})")


def get_router_info() -> dict:
    """
    Retorna informações sobre os routers configurados
    
    Returns:
        Dicionário com informações dos routers
    """
    return {
        "total_routers": len(ROUTER_CONFIG),
        "routers": [
            {
                "prefix": config["prefix"],
                "tags": config["tags"]
            }
            for config in ROUTER_CONFIG
        ]
    }
