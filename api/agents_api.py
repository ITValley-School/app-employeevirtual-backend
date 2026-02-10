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
        logger.error(f"❌ Erro ao listar agentes de sistema: {str(exc)}", exc_info=True)
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
        logger.error(f"❌ Erro ao buscar agente de sistema: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar agente de sistema"
        ) from exc


@router.post("/system/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_system_agent(
    agent_id: str,
    # Aceita tanto JSON quanto multipart/form-data
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
        # Se veio arquivo (multipart/form-data)
        if file:
            logger.info(f"📎 Arquivo recebido: {file.filename} ({file.content_type})")
            
            # Lê conteúdo do arquivo
            file_content = await file.read()
            file_name = file.filename or "arquivo"
            
            # Prepara mensagem (usa a fornecida ou gera uma baseada no tipo)
            if not message:
                content_type = file.content_type or ""
                if content_type.startswith('audio/'):
                    message = "Transcreva este áudio"
                elif content_type.startswith('video/'):
                    message = "Transcreva este vídeo"
                elif content_type.startswith('image/'):
                    message = "Extraia o texto desta imagem"
                elif content_type == 'application/pdf':
                    message = "Processe este PDF"
                else:
                    message = "Processe este arquivo"
            
            # Cria DTO com arquivo no contexto
            # O arquivo será passado como bytes no contexto para as tools processarem
            # Usamos base64 para serializar os bytes de forma mais eficiente
            import base64
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            dto = AgentExecuteRequest(
                message=message,
                session_id=session_id,
                context={
                    "file_content_base64": file_base64,  # Bytes em base64
                    "file_name": file_name,
                    "file_content_type": file.content_type,
                    "file_size": len(file_content),
                    "has_file": True
                }
            )
            
            logger.info(f"✅ Arquivo processado: {file_name} ({len(file_content)} bytes)")
        
        # Se não veio nem arquivo nem DTO, erro
        elif not dto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Envie 'message' (JSON) ou 'file' (multipart/form-data)"
            )
        
        # Executa agente
        result = agent_service.execute_system_agent(agent_id, dto, current_user.id)
        
        # Converte para Response
        return AgentMapper.to_execution_response(
            agent_id=agent_id,
            message=result['message'],
            response=result['response'],
            execution_time=result['execution_time'],
            tokens_used=result['tokens_used'],
            session_id=result.get('session_id')
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"❌ Erro ao executar agente de sistema: {str(exc)}", exc_info=True)
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
        
        # Converte documentos para o formato de resposta
        document_responses = []
        for doc in documents:
            # Garante que created_at existe (deve sempre existir, mas por segurança)
            created_at = doc.get("created_at")
            if not created_at:
                from datetime import datetime
                created_at = datetime.utcnow()
            
            document_responses.append(AgentDocumentResponse(
                id=doc.get("id", str(doc.get("_id", ""))),
                agent_id=doc.get("agent_id", agent_id),
                user_id=doc.get("user_id", current_user.id),
                file_name=doc.get("file_name", ""),
                metadata=doc.get("metadata", {}),
                vector_response=doc.get("vector_response"),
                created_at=created_at,
                updated_at=doc.get("updated_at"),
                mongo_error=doc.get("mongo_error", False)
            ))
        
        return AgentDocumentListResponse(
            documents=document_responses,
            total=len(document_responses),
            agent_id=agent_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"❌ Erro ao listar documentos: {str(exc)}", exc_info=True)
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
        
        return AgentDocumentDeleteResponse(
            success=result.get("success", True),
            document_id=result.get("document_id", document_id),
            file_name=result.get("file_name"),
            vector_db_response=result.get("vector_db_response"),
            mongo_deleted=result.get("mongo_deleted", True),
            message="Documento removido com sucesso"
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"❌ Erro ao deletar documento: {str(exc)}", exc_info=True)
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
        
        doc = result.get("document", {})
        return AgentDocumentResponse(
            id=doc.get("id", str(doc.get("_id", document_id))),
            agent_id=doc.get("agent_id", agent_id),
            user_id=doc.get("user_id", current_user.id),
            file_name=doc.get("file_name", ""),
            metadata=doc.get("metadata", {}),
            vector_response=doc.get("vector_response"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            mongo_error=doc.get("mongo_error", False)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"❌ Erro ao atualizar metadados: {str(exc)}", exc_info=True)
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
