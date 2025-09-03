"""
Configuração de conexão com o banco de dados Azure SQL
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()

# String de conexão Azure SQL
AZURE_SQL_CONNECTION_STRING = os.getenv(
    "AZURE_SQL_CONNECTION_STRING"
)

if not AZURE_SQL_CONNECTION_STRING:
    raise ValueError(
        "AZURE_SQL_CONNECTION_STRING environment variable is not set. "
        "Please configure this variable in your Azure App Service settings."
    )

# Configurações do engine
engine = create_engine(
    AZURE_SQL_CONNECTION_STRING,
    poolclass=StaticPool,  # Para desenvolvimento
    pool_pre_ping=True,    # Verificar conexão antes de usar
    echo=False,            # Set True para ver SQL no console
    future=True            # Usar API v2 do SQLAlchemy
)

# Configuração da sessão
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def get_db():
    """
    Dependency para injetar sessão do banco nas APIs
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """
    Testa conexão com o banco
    """
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT @@VERSION as version")
            version = result.fetchone()
            print(f"✅ Conectado ao Azure SQL Server: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def get_connection_info():
    """
    Retorna informações da conexão
    """
    return {
        "database": engine.url.database,
        "host": engine.url.host,
        "port": engine.url.port,
        "driver": engine.url.drivername
    }

