"""
API de agentes - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
import logging
import requests

from schemas.agents.requests import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentExecuteRequest,
    AgentDocumentMetadataUpdateRequest
)
from schemas.agents.responses import (
    AgentResponse,
    AgentDetailResponse,
    AgentListResponse,
    AgentExecuteResponse,
    AgentDocumentResponse,
    AgentDocumentListResponse,
    AgentDocumentDeleteResponse,
    SystemAgentResponse,
    SystemAgentListResponse
)
from services.agent_service import AgentService
from mappers.agent_mapper import AgentMapper
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
        logger.info(f"Criando agente para usuario {current_user.id}")

        # Service orquestra criação e validações
        agent = agent_service.create_agent(dto, current_user.id)

        logger.info(f"Agente criado com sucesso: {agent.id}")

        # Converte para Response via Mapper
        return AgentMapper.to_public(agent)
    except Exception as e:
        logger.error(f"Erro ao criar agente: {str(e)}", exc_info=True)
        raise


# ========== ENDPOINTS PARA AGENTES DE SISTEMA (DEVEM VIR ANTES DE /{agent_id}) ==========

@router.get("/system", response_model=SystemAgentListResponse)
async def list_system_agents(
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Lista todos os agentes de sistema disponíveis

    Args:
        agent_service: Serviço de agentes
        current_user: Usuário autenticado

    Returns:
        SystemAgentListResponse: Lista de agentes de sistema
    """
    try:
        agents = agent_service.get_system_agents()
        return AgentMapper.to_system_agent_list(agents)
    except Exception as exc:
        logger.error(f"Erro ao listar agentes de sistema: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar agentes de sistema"
        ) from exc


@router.get("/system/{agent_id}", response_model=SystemAgentResponse)
async def get_system_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca agente de sistema por ID

    Args:
        agent_id: ID do agente de sistema
        agent_service: Serviço de agentes
        current_user: Usuário autenticado

    Returns:
        SystemAgentResponse: Dados do agente de sistema
    """
    try:
        agent = agent_service.get_system_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agente de sistema não encontrado ou inativo"
            )
        return AgentMapper.to_system_agent(agent)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao buscar agente de sistema: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar agente de sistema"
        ) from exc


@router.post("/system/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_system_agent(
    agent_id: str,
    dto: Optional[AgentExecuteRequest] = None,
    file: Optional[UploadFile] = File(None, description="Arquivo para processar (áudio, vídeo, imagem ou PDF)"),
    message: Optional[str] = Form(None, description="Mensagem do usuário (usado quando file é enviado)"),
    session_id: Optional[str] = Form(None, description="ID da sessão (usado quando file é enviado)"),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Executa agente de sistema com ferramentas avançadas

    Aceita dois formatos:
    1. JSON: Envie um AgentExecuteRequest com message e session_id
    2. Multipart: Envie file + message (opcional) + session_id (opcional)

    Args:
        agent_id: ID do agente de sistema
        dto: Dados de execução (quando enviado como JSON)
        file: Arquivo para processar (quando enviado como multipart)
        message: Mensagem do usuário (quando file é enviado)
        session_id: ID da sessão (opcional)
        agent_service: Serviço de agentes
        current_user: Usuário autenticado

    Returns:
        AgentExecuteResponse: Resultado da execução
    """
    try:
        # Se veio arquivo, delega construção do DTO para o Service
        if file:
            file_content = await file.read()
            dto = agent_service.build_execute_request_from_file(
                file_content=file_content,
                file_name=file.filename or "arquivo",
                content_type=file.content_type,
                message=message,
                session_id=session_id,
            )
        elif not dto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Envie 'message' (JSON) ou 'file' (multipart/form-data)"
            )

        # Service orquestra execução
        result = agent_service.execute_system_agent(agent_id, dto, current_user.id)

        # Converte para Response via Mapper (recebe dict inteiro)
        return AgentMapper.to_execution_response(result, agent_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao executar agente de sistema: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao executar agente de sistema"
        ) from exc


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

    # Converte para Response via Mapper
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

    # Converte para Response via Mapper
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
        error_msg = str(exc)
        if result and result.get("vector_db_response"):
            logger.warning(
                f"Documento enviado para Vector DB mas falhou ao registrar no MongoDB: {error_msg}"
            )
            return AgentMapper.to_upload_response(result)
        logger.exception("Erro inesperado ao enviar PDF para Vector DB")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado ao enviar documento") from exc

    # Converte para Response via Mapper
    return AgentMapper.to_upload_response(result)


@router.get("/{agent_id}/documents", response_model=AgentDocumentListResponse)
async def list_agent_documents(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Lista documentos associados a um agente.

    Args:
        agent_id: ID do agente
        agent_service: Serviço de agentes
        current_user: Usuário autenticado

    Returns:
        AgentDocumentListResponse: Lista de documentos do agente
    """
    try:
        documents = agent_service.list_agent_documents(agent_id, current_user.id)

        # Converte para Response via Mapper
        return AgentMapper.to_document_list(documents, agent_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Erro ao listar documentos: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar documentos"
        ) from exc


@router.delete("/{agent_id}/documents/{document_id}", response_model=AgentDocumentDeleteResponse)
async def delete_agent_document(
    agent_id: str,
    document_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Remove um documento do agente (MongoDB + Pinecone).

    Args:
        agent_id: ID do agente
        document_id: ID do documento
        agent_service: Serviço de agentes
        current_user: Usuário autenticado

    Returns:
        AgentDocumentDeleteResponse: Resultado da deleção
    """
    try:
        result = agent_service.delete_agent_document(
            agent_id=agent_id,
            document_id=document_id,
            user_id=current_user.id
        )

        # Converte para Response via Mapper
        return AgentMapper.to_document_delete(result, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Erro ao deletar documento: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar documento"
        ) from exc


@router.patch("/{agent_id}/documents/{document_id}/metadata", response_model=AgentDocumentResponse)
async def update_agent_document_metadata(
    agent_id: str,
    document_id: str,
    dto: AgentDocumentMetadataUpdateRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Atualiza metadados de um documento do agente.

    Args:
        agent_id: ID do agente
        document_id: ID do documento
        dto: Dados de atualização de metadados
        agent_service: Serviço de agentes
        current_user: Usuário autenticado

    Returns:
        AgentDocumentResponse: Documento atualizado
    """
    try:
        result = agent_service.update_agent_document_metadata(
            agent_id=agent_id,
            document_id=document_id,
            user_id=current_user.id,
            metadata_updates=dto.metadata
        )

        # Converte para Response via Mapper
        doc = result.get("document", {})
        return AgentMapper.to_document(doc, agent_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Erro ao atualizar metadados: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar metadados"
        ) from exc


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

    # Converte para Response via Mapper
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

    # Converte para Response via Mapper (recebe dict inteiro)
    return AgentMapper.to_execution_response(result, agent_id)


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
