"""
Factory para chat
Cria objetos do domínio seguindo padrão IT Valley Architecture
"""
from typing import Optional
from datetime import datetime
from uuid import uuid4

from schemas.chat.requests import ChatMessageRequest, ChatSessionRequest
from domain.chat.chat_entity import ChatEntity


class ChatFactory:
    """Factory para criação de chat"""
    
    @staticmethod
    def create_session(dto: ChatSessionRequest, user_id: str) -> ChatEntity:
        """
        Cria sessão de chat
        
        Args:
            dto: Dados da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão criada
        """
        return ChatEntity(
            id=str(uuid4()),
            title=dto.title,
            user_id=user_id,
            status="active",
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def create_message(dto: ChatMessageRequest, session_id: str, user_id: str) -> ChatEntity:
        """
        Cria mensagem de chat
        
        Args:
            dto: Dados da mensagem
            session_id: ID da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Mensagem criada
        """
        return ChatEntity(
            id=str(uuid4()),
            session_id=session_id,
            user_id=user_id,
            message=dto.message,
            role="user",
            created_at=datetime.utcnow()
        )
