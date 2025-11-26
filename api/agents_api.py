"""
API de agentes - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
import logging
import requests

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

logger = logging.getLogger(__name__)
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
    try:
        logger.info(f"📝 Criando agente: {dto.name} para usuário {current_user.id}")
        logger.debug(f"   name={dto.name} (type: {type(dto.name).__name__})")
        logger.debug(f"   type={dto.type} (value: {dto.type.value if hasattr(dto.type, 'value') else dto.type})")
        logger.debug(f"   instructions={dto.instructions} (len: {len(dto.instructions)})")
        logger.debug(f"   temperature={dto.temperature} (type: {type(dto.temperature).__name__ if dto.temperature else 'None'})")
        logger.debug(f"   max_tokens={dto.max_tokens} (type: {type(dto.max_tokens).__name__ if dto.max_tokens else 'None'})")
        logger.debug(f"   model={dto.model} (type: {type(dto.model).__name__ if dto.model else 'None'})")
        
        # 1. Cria agente via Service (Service orquestra tudo)
        agent = agent_service.create_agent(dto, current_user.id)
        
        logger.info(f"✅ Agente criado com sucesso: {agent.id}")
        
        # 2. Converte para Response via Mapper
        return AgentMapper.to_public(agent)
    except Exception as e:
        logger.error(f"❌ Erro ao criar agente: {str(e)}", exc_info=True)
        raise


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
    result = agent_service.get_agent_detail(agent_id, current_user.id)
    
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
    agent = agent_service.update_agent(agent_id, dto, current_user.id)
    
    # Converte para Response
    return AgentMapper.to_public(agent)


@router.post("/{agent_id}/documents", status_code=status.HTTP_201_CREATED)
async def upload_agent_document(
    agent_id: str,
    filepdf: UploadFile = File(..., description="Arquivo PDF com o conhecimento do agente"),
    metadone: Optional[str] = Form(None, description="JSON com metadados adicionais"),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Faz upload de um PDF para o serviço vetorial e o associa ao agente.
    """
    file_bytes = await filepdf.read()
    result = None
    try:
        result = agent_service.upload_agent_document(
            agent_id=agent_id,
            user_id=current_user.id,
            file_content=file_bytes,
            file_name=filepdf.filename or "documento.pdf",
            content_type=filepdf.content_type,
            metadata_raw=metadone,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except requests.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Erro ao comunicar com Vector DB: {detail}") from exc
    except Exception as exc:
        # Se o documento foi enviado para o Vector DB mas falhou no MongoDB,
        # ainda retornamos sucesso (o documento está no Pinecone)
        error_msg = str(exc)
        if result and result.get("vector_db_response"):
            logger.warning(
                f"⚠️ Documento enviado para Vector DB mas falhou ao registrar no MongoDB: {error_msg}"
            )
            # Retorna sucesso parcial - documento está no Pinecone
            return {
                "message": "Documento enviado com sucesso para Vector DB. Aviso: falha ao registrar no MongoDB.",
                "document": {"mongo_error": True, "message": "Documento no Pinecone mas não registrado no MongoDB"},
                "vector_db_response": result.get("vector_db_response"),
                "warning": "MongoDB indisponível, mas documento está no Vector DB"
            }
        logger.exception("Erro inesperado ao enviar PDF para Vector DB")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado ao enviar documento") from exc

    # Verifica se houve erro no MongoDB mas documento foi enviado
    document = result.get("document", {}) if result else {}
    if document.get("mongo_error"):
        logger.warning("⚠️ Documento enviado para Vector DB mas não registrado no MongoDB (timeout)")
        return {
            "message": "Documento enviado com sucesso para Vector DB. Aviso: falha ao registrar no MongoDB.",
            "document": document,
            "vector_db_response": result.get("vector_db_response") if result else None,
            "warning": "MongoDB indisponível, mas documento está no Vector DB"
        }

    return {
        "message": "Documento enviado com sucesso",
        "document": document,
        "vector_db_response": result.get("vector_db_response") if result else None
    }


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
    agents, total = agent_service.list_agents(current_user.id, page, size, status)
    
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
    result = agent_service.execute_agent(agent_id, dto, current_user.id)
    
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
    agent = agent_service.activate_agent(agent_id, current_user.id)
    
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
    agent = agent_service.deactivate_agent(agent_id, current_user.id)
    
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
    agent = agent_service.start_training(agent_id, current_user.id)
    
    return AgentMapper.to_public(agent)
