"""
Aplicação principal do sistema EmployeeVirtual
"""
from fastapi import FastAPI
from dotenv import load_dotenv
import logging

from api.router_config import register_routers
from data.migrations import auto_migrate, get_status, test_db
from middlewares.cors_middleware import add_cors_middleware

# Importa todos os modelos para registro na base
import models

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

# @app.on_event("startup")
# async def startup_event():
#     """
#     Evento executado na inicialização da aplicação
#     """
#     logger.info("🚀 Iniciando EmployeeVirtual API...")
    
#     # Testar conexão com banco
#     if test_db():
#         logger.info("✅ Conexão com banco estabelecida")
        
#         # Executar auto-migração
#         try:
#             logger.info("🔄 Executando auto-migração do banco...")
#             success = auto_migrate()
            
#             if success:
#                 logger.info("✅ Auto-migração concluída com sucesso!")
                
#                 # Mostrar status final
#                 status = get_status()
#                 logger.info(f"📊 Status do banco: {status}")
                
#             else:
#                 logger.error("❌ Falha na auto-migração!")
                
#         except Exception as e:
#             logger.error(f"💥 Erro durante auto-migração: {e}")
#     else:
#         logger.error("❌ Falha na conexão com banco de dados")
    
#     logger.info("🎯 EmployeeVirtual API pronta para uso!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação
    """
    logger.info("🛑 Encerrando EmployeeVirtual API...")


