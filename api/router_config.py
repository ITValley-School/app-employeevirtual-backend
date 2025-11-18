"""
Configuração centralizada de routers da API EmployeeVirtual
"""
from fastapi import FastAPI

# Imports dos routers - IT Valley Architecture
from api.auth_api import router as auth_router
from api.users_api import router as users_router
from api.agents_api import router as agents_router
from api.flows_api import router as flows_router
from api.chat_api import router as chat_router
from api.dashboard_api import router as dashboard_router
from api.metadata_api import router as metadata_router

# Configuração das rotas
ROUTER_CONFIG = [
    {
        "router": auth_router,
        "prefix": "/api",
        "tags": ["Autenticação"]
    },
    {
        "router": users_router,
        "prefix": "/api",
        "tags": ["Usuários"]
    },
    {
        "router": agents_router,
        "prefix": "/api",
        "tags": ["Agentes"]
    },
    {
        "router": flows_router,
        "prefix": "/api",
        "tags": ["Flows"]
    },
    {
        "router": chat_router,
        "prefix": "/api",
        "tags": ["Chat"]
    },
    {
        "router": dashboard_router,
        "prefix": "/api",
        "tags": ["Dashboard"]
    },
    {
        "router": metadata_router,
        "prefix": "/api",
        "tags": ["Metadados"]
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
        print(f"[OK] Router registrado: {config['prefix']} ({', '.join(config['tags'])})")


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
