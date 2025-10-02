"""
Mapper para chat
Converte entre Entity (domínio) e Response (API)
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List
from datetime import datetime

from schemas.chat.responses import (
    ChatMessageResponse, 
    ChatSessionResponse, 
    ChatListResponse,
    ChatHistoryResponse
)
from domain.chat.chat_entity import ChatEntity


class ChatMapper:
    """Mapper para conversão de chat"""
    
    @staticmethod
    def to_message(chat: ChatEntity) -> ChatMessageResponse:
        """
        Converte ChatEntity para ChatMessageResponse
        
        Args:
            chat: Entidade do domínio
            
        Returns:
            ChatMessageResponse: Mensagem formatada
        """
        return ChatMessageResponse(
            id=chat.id,
            chat_id=chat.session_id or chat.id,
            type=chat.role,
            content=chat.message or "",
            timestamp=chat.created_at,
            metadata={}
        )
    
    @staticmethod
    def to_session(chat: ChatEntity) -> ChatSessionResponse:
        """
        Converte ChatEntity para ChatSessionResponse
        
        Args:
            chat: Entidade do domínio
            
        Returns:
            ChatSessionResponse: Sessão formatada
        """
        return ChatSessionResponse(
            id=chat.id,
            title=chat.title or "Nova Sessão",
            user_id=chat.user_id,
            status=chat.status,
            created_at=chat.created_at
        )
    
    @staticmethod
    def to_list(sessions: List[ChatEntity], total: int, page: int, size: int) -> ChatListResponse:
        """
        Converte lista de ChatEntity para ChatListResponse
        
        Args:
            sessions: Lista de entidades do domínio
            total: Total de sessões
            page: Página atual
            size: Tamanho da página
            
        Returns:
            ChatListResponse: Lista formatada para API
        """
        return ChatListResponse(
            chats=[ChatMapper.to_session(session) for session in sessions],
            total=total,
            page=page,
            size=size
        )
    
    @staticmethod
    def to_history(messages: List[ChatEntity], total: int, page: int, size: int) -> ChatHistoryResponse:
        """
        Converte lista de mensagens para ChatHistoryResponse
        
        Args:
            messages: Lista de mensagens
            total: Total de mensagens
            page: Página atual
            size: Tamanho da página
            
        Returns:
            ChatHistoryResponse: Histórico formatado
        """
        return ChatHistoryResponse(
            messages=[ChatMapper.to_message(msg) for msg in messages],
            total=total,
            page=page,
            size=size
        )
