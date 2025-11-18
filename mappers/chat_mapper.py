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
    ChatHistoryResponse,
    ChatHistoryMessageResponse,
    ChatSendResponse
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
            type=chat.sender,  # Mudado de chat.role para chat.sender
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
        Formata para ser compatível com MongoDB (usa 'sender' em vez de 'type')
        
        Args:
            messages: Lista de mensagens (ChatEntity)
            total: Total de mensagens
            page: Página atual
            size: Tamanho da página
            
        Returns:
            ChatHistoryResponse: Histórico formatado com mensagens
        """
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(
                ChatHistoryMessageResponse(
                    id=msg.id,
                    message=msg.message or "",
                    sender=msg.sender,  # 'user' ou 'assistant'
                    created_at=msg.created_at,
                    context=msg.context or {},
                    metadata={}
                )
            )
        
        return ChatHistoryResponse(
            messages=formatted_messages,
            total=total,
            page=page,
            size=size
        )
    
    @staticmethod
    def to_send_response(data: dict) -> ChatSendResponse:
        """
        Converte resultado de envio de mensagem para ChatSendResponse
        
        Args:
            data: Dicionário com 'user_message' e 'assistant_response'
            
        Returns:
            ChatSendResponse: Response formatada
        """
        user_msg = data.get('user_message')
        asst_msg = data.get('assistant_response')
        
        return ChatSendResponse(
            message=user_msg.message if user_msg else "",
            response=asst_msg.message if asst_msg else "",
            message_id=user_msg.id if user_msg else "",
            response_id=asst_msg.id if asst_msg else "",
            timestamp=asst_msg.created_at if asst_msg else datetime.utcnow(),
            metadata={}
        )
