"""
Configuração de conexão com banco de dados
"""
import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from typing import Generator
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
def get_database_url():
    """
    Constrói a URL de conexão do banco de dados
    """
    # Primeiro tenta usar a DATABASE_URL completa
    database_url = os.getenv("DATABASE_URL_PYODBC")
    if database_url:
        return database_url
    
    # Se não tiver DATABASE_URL, constrói a partir das variáveis individuais
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE") 
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    driver = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
    port = os.getenv("SQL_PORT", "1433")
    
    if not all([server, database, username, password]):
        raise ValueError(
            "Configuração de banco de dados incompleta. "
            "Configure DATABASE_URL ou todas as variáveis SQL_* no arquivo .env"
        )
    
    # Construir URL de conexão para Azure SQL
    return (
        f"mssql+pyodbc://{username}:{password}@{server}:{port}/{database}"
        f"?driver={driver.replace(' ', '+')}"
        f"&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
    )

DATABASE_URL = get_database_url()

# Configuração do engine para SQL Server/Azure
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Metadata com schema
metadata = MetaData(schema="empl")

def get_db() -> Generator:
    """
    Dependency para obter sessão do banco de dados
    
    Yields:
        Session: Sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """
    Testa a conexão com o banco de dados
    
    Returns:
        bool: True se conexão bem-sucedida
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.fetchone() is not None
    except Exception as e:
        raise ConnectionError(f"Erro ao conectar com banco de dados: {e}")

def get_connection_info():
    """
    Retorna informações da conexão (sem credenciais)
    
    Returns:
        Dict com informações da conexão
    """
    try:
        with engine.connect() as connection:
            # Testar conexão
            connection.execute(text("SELECT 1"))
            
        return {
            "status": "connected",
            "driver": "SQL Server",
            "database": os.getenv("SQL_DATABASE", "N/A"),
            "server": os.getenv("SQL_SERVER", "N/A"),
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "checked_in": engine.pool.checkedin()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database": os.getenv("SQL_DATABASE", "N/A"),
            "server": os.getenv("SQL_SERVER", "N/A")
        }

# Funções para administração (use com cuidado)
def create_tables():
    """
    Cria todas as tabelas no banco de dados
    ATENÇÃO: Use apenas se necessário e você tem certeza!
    """
    print("⚠️ ATENÇÃO: Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso")

def drop_tables():
    """
    Remove todas as tabelas do banco de dados
    ATENÇÃO: Esta operação é IRREVERSÍVEL!
    """
    print("⚠️ PERIGO: Removendo todas as tabelas...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tabelas removidas")

