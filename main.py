"""
Aplicação principal do sistema EmployeeVirtual
"""
from fastapi import FastAPI
from dotenv import load_dotenv
import logging

from api.router_config import register_routers
# from data.migrations import auto_migrate, get_status, test_db  # Comentado para evitar problemas de importação
from middlewares.cors_middleware import add_cors_middleware

# Importa todos os modelos para registro na base
# import models  # Removido para evitar problemas de importação circular

# Carrega variáveis de ambiente
load_dotenv()

# Configura logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("azure").setLevel(logging.WARNING)

# Inicializa FastAPI
app = FastAPI()

# Configura CORS via middleware dedicado
add_cors_middleware(app)

# Registrar todos os routers automaticamente
register_routers(app)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação
    """
    logger.info("Encerrando EmployeeVirtual API...")


