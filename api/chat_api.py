"""
API de chat - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
import logging

from schemas.chat.requests import ChatMessageRequest, ChatSessionRequest
from schemas.chat.responses import (
    ChatMessageResponse, 
    ChatSessionResponse, 
    ChatListResponse,
    ChatHistoryResponse,
    ChatSendResponse,
    AgentConversationsResponse,
    ConversationSidebarItem
)
from services.chat_service import ChatService
from mappers.chat_mapper import ChatMapper
from factories.chat_factory import ChatFactory
from config.database import db_config
from auth.dependencies import get_current_user
from data.entities.user_entities import UserEntity

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: Session = Depends(db_config.get_session)) -> ChatService:
    """Dependency para ChatService"""
    return ChatService(db)


@router.post("/sessions", response_model=ConversationSidebarItem, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    dto: ChatSessionRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Cria nova sessão de chat
    
    Args:
        dto: Dados da sessão
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        ConversationSidebarItem: Conversa criada com dados para sidebar
    """
    # Service orquestra criação e validações
    session = chat_service.create_session(dto, current_user.id)
    
    # Converte para Response do sidebar (com metadados completos)
    return ConversationSidebarItem(
        id=session.id,
        title=session.title,
        agent_id=session.agent_id,
        user_id=current_user.id,
        message_count=0,  # Nova conversa tem 0 mensagens
        status="active",
        last_activity=session.created_at,
        created_at=session.created_at
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatSendResponse)
async def send_message(
    session_id: str,
    dto: ChatMessageRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Envia mensagem para o chat
    
    Args:
        session_id: ID da sessão
        dto: Dados da mensagem
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        ChatSendResponse: Mensagem enviada e resposta do assistente
    """
    # Service orquestra envio e validações (assíncrono)
    result = await chat_service.send_message_async(session_id, dto, current_user.id)
    
    # Converte para Response - result agora é um dicionário com 'user_message' e 'assistant_response'
    return ChatMapper.to_send_response(result)


@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca histórico de mensagens da sessão
    
    Args:
        session_id: ID da sessão
        page: Página
        size: Tamanho da página
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        ChatHistoryResponse: Histórico de mensagens
    """
    # Service orquestra busca e validações
    messages, total = chat_service.get_chat_history(session_id, current_user.id, page, size)
    
    # Converte para Response
    return ChatMapper.to_history(messages, total, page, size)


@router.get("/sessions", response_model=ChatListResponse)
async def list_chat_sessions(
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Lista sessões de chat do usuário
    
    Args:
        page: Página
        size: Tamanho da página
        status: Filtro por status
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        ChatListResponse: Lista de sessões
    """
    # Lista sessões
    sessions, total = chat_service.list_sessions(current_user.id, page, size, status)
    
    # Converte para Response
    return ChatMapper.to_list(sessions, total, page, size)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca sessão de chat por ID
    
    Args:
        session_id: ID da sessão
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        ChatSessionResponse: Dados da sessão
    """
    # Service orquestra busca e validações
    session = chat_service.get_session(session_id, current_user.id)
    
    # Converte para Response
    return ChatMapper.to_session(session)


@router.patch("/sessions/{session_id}/close", response_model=ChatSessionResponse)
async def close_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Fecha sessão de chat
    
    Args:
        session_id: ID da sessão
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        ChatSessionResponse: Sessão fechada
    """
    # Service orquestra fechamento e validações
    session = chat_service.close_session(session_id, current_user.id)
    
    return ChatMapper.to_session(session)


@router.get("/agents/{agent_id}/conversations", response_model=AgentConversationsResponse)
async def get_agent_conversations(
    agent_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca todas as conversas ativas de um agente para a sidebar
    
    Args:
        agent_id: ID do agente
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        AgentConversationsResponse: Conversas ativas do agente
    """
    # Busca conversas do agente no MongoDB
    conversations = chat_service.get_agent_conversations(agent_id, current_user.id)
    
    return AgentConversationsResponse(
        agent_id=agent_id,
        conversations=conversations,
        total=len(conversations)
    )


@router.patch("/sessions/{session_id}/inactivate", status_code=status.HTTP_200_OK)
async def inactivate_conversation_sql(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Inativa conversa no SQL Server
    
    Args:
        session_id: ID da sessão
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        dict: Mensagem de sucesso
    """
    chat_service.inactivate_conversation_sql(session_id, current_user.id)
    return {"message": "Conversa inativada no SQL Server"}


@router.patch("/conversations/{conversation_id}/inactivate", status_code=status.HTTP_200_OK)
async def inactivate_conversation_mongo(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Inativa conversa no MongoDB
    
    Args:
        conversation_id: ID da conversa (MongoDB)
        chat_service: Serviço de chat
        current_user: Usuário autenticado
        
    Returns:
        dict: Mensagem de sucesso
    """
    try:
        chat_service.inactivate_conversation_mongo(conversation_id, current_user.id)
        return {"message": "Conversa inativada no MongoDB"}
    except Exception as e:
        logger.error(f"Erro ao inativar conversa: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao inativar conversa: {str(e)}"
        )

