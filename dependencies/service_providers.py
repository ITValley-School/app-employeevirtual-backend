"""
Provedores de serviços para injeção de dependência
Responsável por criar instâncias dos serviços com suas dependências
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from services.agent_service import AgentService
from services.chat_service import ChatService
from services.user_service import UserService
from services.dashboard_service import DashboardService
from services.flow_service import FlowService
from services.file_service import FileService
from services.llm_key_service import LLMKeyService
from services.system_agent_service import CatalogService
from data.database import get_db


def get_agent_service(db: Session = Depends(get_db)) -> AgentService:
    """
    Provedor do AgentService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do AgentService
    """
    return AgentService(db)


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """
    Provedor do ChatService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do ChatService
    """
    return ChatService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Provedor do UserService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do UserService
    """
    return UserService(db)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """
    Provedor do DashboardService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do DashboardService
    """
    return DashboardService(db)


def get_flow_service(db: Session = Depends(get_db)) -> FlowService:
    """
    Provedor do FlowService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do FlowService
    """
    return FlowService(db)


def get_file_service(db: Session = Depends(get_db)) -> FileService:
    """
    Provedor do FileService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do FileService
    """
    return FileService(db)


def get_llm_key_service(db: Session = Depends(get_db)) -> LLMKeyService:
    """
    Provedor do LLMKeyService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do LLMKeyService
    """
    return LLMKeyService(db)


def get_catalog_service(db: Session = Depends(get_db)) -> CatalogService:
    """
    Provedor do CatalogService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do CatalogService
    """
    return CatalogService(db)
