"""
Configuração centralizada de routers da API EmployeeVirtual
"""
from fastapi import FastAPI

# Imports dos routers - IT Valley Architecture
from api.users_api import router as users_router
from api.agents_api import router as agents_router

# Configuração das rotas
ROUTER_CONFIG = [
    {
        "router": users_router,
        "prefix": "/api",
        "tags": ["Usuários"]
    },
    {
        "router": agents_router,
        "prefix": "/api",
        "tags": ["Agentes"]
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
