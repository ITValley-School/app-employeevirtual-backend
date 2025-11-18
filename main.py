"""
Aplicação principal do sistema EmployeeVirtual
"""
from fastapi import FastAPI
from dotenv import load_dotenv
import logging

# Carrega variáveis de ambiente PRIMEIRO
load_dotenv()

from api.router_config import register_routers
# from data.migrations import auto_migrate, get_status, test_db  # Comentado para evitar problemas de importação
from middlewares.cors_middleware import add_cors_middleware

# Importa todos os modelos para registro na base
# import models  # Removido para evitar problemas de importação circular

# Configura logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("azure").setLevel(logging.WARNING)

# Inicializa FastAPI
app = FastAPI()

# Configura CORS via middleware dedicado PRIMEIRO (antes dos routers)
add_cors_middleware(app)

# Registrar todos os routers automaticamente DEPOIS
register_routers(app)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação
    """
    logger.info("Encerrando EmployeeVirtual API...")


