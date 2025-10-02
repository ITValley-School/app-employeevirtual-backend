"""
API de agentes - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from sqlalchemy.orm import Session

from schemas.agents.requests import AgentCreateRequest, AgentUpdateRequest, AgentExecuteRequest
from schemas.agents.responses import (
    AgentResponse, 
    AgentDetailResponse, 
    AgentListResponse,
    AgentExecuteResponse
)
from services.agent_service import AgentService
from mappers.agent_mapper import AgentMapper
from factories.agent_factory import AgentFactory
from config.database import db_config
from auth.dependencies import get_current_user
from data.entities.user_entities import UserEntity

router = APIRouter(prefix="/agents", tags=["agents"])


def get_agent_service(db: Session = Depends(db_config.get_session)) -> AgentService:
    """Dependency para AgentService"""
    return AgentService(db)


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    dto: AgentCreateRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Cria novo agente
    
    Args:
        dto: Dados do agente
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentResponse: Agente criado
    """
    # 1. Cria agente via Service (Service orquestra tudo)
    agent = agent_service.create_agent(dto, current_user.get_id())
    
    # 2. Converte para Response via Mapper
    return AgentMapper.to_public(agent)


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca agente por ID
    
    Args:
        agent_id: ID do agente
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentDetailResponse: Dados detalhados do agente
    """
    # Service orquestra busca e validações
    result = agent_service.get_agent_detail(agent_id, current_user.get_id())
    
    # Converte para Response
    return AgentMapper.to_detail(result['agent'], result['stats'])


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    dto: AgentUpdateRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Atualiza agente
    
    Args:
        agent_id: ID do agente
        dto: Dados para atualização
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentResponse: Agente atualizado
    """
    # Service orquestra atualização e validações
    agent = agent_service.update_agent(agent_id, dto, current_user.get_id())
    
    # Converte para Response
    return AgentMapper.to_public(agent)


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Lista agentes do usuário
    
    Args:
        page: Página
        size: Tamanho da página
        status: Filtro por status
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentListResponse: Lista de agentes
    """
    # Lista agentes
    agents, total = agent_service.list_agents(current_user.get_id(), page, size, status)
    
    # Converte para Response
    return AgentMapper.to_list(agents, total, page, size)


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    dto: AgentExecuteRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Executa agente
    
    Args:
        agent_id: ID do agente
        dto: Dados de execução
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentExecuteResponse: Resultado da execução
    """
    # Service orquestra execução e validações
    result = agent_service.execute_agent(agent_id, dto, current_user.get_id())
    
    # Converte para Response
    return AgentMapper.to_execution_response(
        agent_id=agent_id,
        message=result['message'],
        response=result['response'],
        execution_time=result['execution_time'],
        tokens_used=result['tokens_used'],
        session_id=result['session_id']
    )


@router.patch("/{agent_id}/activate", response_model=AgentResponse)
async def activate_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Ativa agente
    
    Args:
        agent_id: ID do agente
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentResponse: Agente ativado
    """
    # Service orquestra ativação e validações
    agent = agent_service.activate_agent(agent_id, current_user.get_id())
    
    return AgentMapper.to_public(agent)


@router.patch("/{agent_id}/deactivate", response_model=AgentResponse)
async def deactivate_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Desativa agente
    
    Args:
        agent_id: ID do agente
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentResponse: Agente desativado
    """
    # Service orquestra desativação e validações
    agent = agent_service.deactivate_agent(agent_id, current_user.get_id())
    
    return AgentMapper.to_public(agent)


@router.post("/{agent_id}/train", response_model=AgentResponse)
async def start_training(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Inicia treinamento do agente
    
    Args:
        agent_id: ID do agente
        agent_service: Serviço de agentes
        current_user: Usuário autenticado
        
    Returns:
        AgentResponse: Agente em treinamento
    """
    # Service orquestra treinamento e validações
    agent = agent_service.start_training(agent_id, current_user.get_id())
    
    return AgentMapper.to_public(agent)
