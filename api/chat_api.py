"""
API de chat - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from sqlalchemy.orm import Session

from schemas.chat.requests import ChatMessageRequest, ChatSessionRequest
from schemas.chat.responses import (
    ChatMessageResponse, 
    ChatSessionResponse, 
    ChatListResponse,
    ChatHistoryResponse
)
from services.chat_service import ChatService
from mappers.chat_mapper import ChatMapper
from factories.chat_factory import ChatFactory
from config.database import db_config
from auth.dependencies import get_current_user
from data.entities.user_entities import UserEntity

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: Session = Depends(db_config.get_session)) -> ChatService:
    """Dependency para ChatService"""
    return ChatService(db)


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
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
        ChatSessionResponse: Sessão criada
    """
    # Service orquestra criação e validações
    session = chat_service.create_session(dto, current_user.get_id())
    
    # Converte para Response via Mapper
    return ChatMapper.to_session(session)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
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
        ChatMessageResponse: Mensagem enviada
    """
    # Service orquestra envio e validações
    message = chat_service.send_message(session_id, dto, current_user.get_id())
    
    # Converte para Response
    return ChatMapper.to_message(message)


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
    messages, total = chat_service.get_chat_history(session_id, current_user.get_id(), page, size)
    
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
    sessions, total = chat_service.list_sessions(current_user.get_id(), page, size, status)
    
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
    session = chat_service.get_session(session_id, current_user.get_id())
    
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
    session = chat_service.close_session(session_id, current_user.get_id())
    
    return ChatMapper.to_session(session)
