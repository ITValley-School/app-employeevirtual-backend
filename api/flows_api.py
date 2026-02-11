"""
API de flows - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from sqlalchemy.orm import Session

from schemas.flows.requests import FlowCreateRequest, FlowUpdateRequest, FlowExecuteRequest
from schemas.flows.responses import (
    FlowResponse, 
    FlowDetailResponse, 
    FlowListResponse,
    FlowExecuteResponse
)
from services.flow_service import FlowService
from mappers.flow_mapper import FlowMapper
from config.database import db_config
from auth.dependencies import get_current_user
from data.entities.user_entities import UserEntity

router = APIRouter(prefix="/flows", tags=["flows"])


def get_flow_service(db: Session = Depends(db_config.get_session)) -> FlowService:
    """Dependency para FlowService"""
    return FlowService(db)


@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    dto: FlowCreateRequest,
    flow_service: FlowService = Depends(get_flow_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Cria novo flow
    
    Args:
        dto: Dados do flow
        flow_service: Serviço de flows
        current_user: Usuário autenticado
        
    Returns:
        FlowResponse: Flow criado
    """
    # Service orquestra criação e validações
    flow = flow_service.create_flow(dto, current_user.id)
    
    # Converte para Response via Mapper
    return FlowMapper.to_public(flow)


@router.get("/{flow_id}", response_model=FlowDetailResponse)
async def get_flow(
    flow_id: str,
    flow_service: FlowService = Depends(get_flow_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca flow por ID
    
    Args:
        flow_id: ID do flow
        flow_service: Serviço de flows
        current_user: Usuário autenticado
        
    Returns:
        FlowDetailResponse: Dados detalhados do flow
    """
    # Service orquestra busca e validações
    result = flow_service.get_flow_detail(flow_id, current_user.id)
    
    # Converte para Response
    return FlowMapper.to_detail(result['flow'], result['stats'])


@router.put("/{flow_id}", response_model=FlowResponse)
async def update_flow(
    flow_id: str,
    dto: FlowUpdateRequest,
    flow_service: FlowService = Depends(get_flow_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Atualiza flow
    
    Args:
        flow_id: ID do flow
        dto: Dados para atualização
        flow_service: Serviço de flows
        current_user: Usuário autenticado
        
    Returns:
        FlowResponse: Flow atualizado
    """
    # Service orquestra atualização e validações
    flow = flow_service.update_flow(flow_id, dto, current_user.id)
    
    # Converte para Response
    return FlowMapper.to_public(flow)


@router.get("/", response_model=FlowListResponse)
async def list_flows(
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    flow_service: FlowService = Depends(get_flow_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Lista flows do usuário
    
    Args:
        page: Página
        size: Tamanho da página
        status: Filtro por status
        flow_service: Serviço de flows
        current_user: Usuário autenticado
        
    Returns:
        FlowListResponse: Lista de flows
    """
    # Lista flows
    flows, total = flow_service.list_flows(current_user.id, page, size, status)
    
    # Converte para Response
    return FlowMapper.to_list(flows, total, page, size)


@router.post("/{flow_id}/execute", response_model=FlowExecuteResponse)
async def execute_flow(
    flow_id: str,
    dto: FlowExecuteRequest,
    flow_service: FlowService = Depends(get_flow_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Executa flow
    
    Args:
        flow_id: ID do flow
        dto: Dados de execução
        flow_service: Serviço de flows
        current_user: Usuário autenticado
        
    Returns:
        FlowExecuteResponse: Resultado da execução
    """
    # Service orquestra execução e validações
    result = flow_service.execute_flow(flow_id, dto, current_user.id)

    # Converte para Response via Mapper (recebe dict inteiro)
    return FlowMapper.to_execution_response(result, flow_id)


@router.patch("/{flow_id}/activate", response_model=FlowResponse)
async def activate_flow(
    flow_id: str,
    flow_service: FlowService = Depends(get_flow_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Ativa flow
    
    Args:
        flow_id: ID do flow
        flow_service: Serviço de flows
        current_user: Usuário autenticado
        
    Returns:
        FlowResponse: Flow ativado
    """
    # Service orquestra ativação e validações
    flow = flow_service.activate_flow(flow_id, current_user.id)
    
    return FlowMapper.to_public(flow)


@router.patch("/{flow_id}/deactivate", response_model=FlowResponse)
async def deactivate_flow(
    flow_id: str,
    flow_service: FlowService = Depends(get_flow_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Desativa flow
    
    Args:
        flow_id: ID do flow
        flow_service: Serviço de flows
        current_user: Usuário autenticado
        
    Returns:
        FlowResponse: Flow desativado
    """
    # Service orquestra desativação e validações
    flow = flow_service.deactivate_flow(flow_id, current_user.id)
    
    return FlowMapper.to_public(flow)
