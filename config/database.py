"""
Configurações de banco de dados
Seguindo padrão IT Valley Architecture
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from config.settings import settings


class DatabaseConfig:
    """
    Configuração do banco de dados
    """
    
    def __init__(self):
        self.engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self) -> Generator:
        """
        Gera sessão do banco de dados
        
        Yields:
            Session: Sessão do SQLAlchemy
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def create_tables(self):
        """
        Cria tabelas do banco de dados
        """
        from data.entities import user_entities  # Importa para registrar
        # Adicione outros imports conforme necessário
        
        # Cria todas as tabelas
        user_entities.Base.metadata.create_all(bind=self.engine)


# Instância global
db_config = DatabaseConfig()
