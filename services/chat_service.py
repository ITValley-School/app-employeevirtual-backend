"""
Service de chat - Orquestrador de casos de uso
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from schemas.chat.requests import ChatMessageRequest, ChatSessionRequest
from domain.chat.chat_entity import ChatEntity
from factories.chat_factory import ChatFactory
from data.chat_repository import ChatRepository


class ChatService:
    """Service para orquestração de chat"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chat_repository = ChatRepository(db)
    
    def create_session(self, dto: ChatSessionRequest, user_id: str) -> ChatEntity:
        """
        Cria nova sessão de chat
        
        Args:
            dto: Dados da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão criada
        """
        # 1. Factory cria Entity a partir do DTO
        session = ChatFactory.create_session(dto, user_id)
        
        # 2. Repository persiste Entity
        self.chat_repository.add_session(session)
        
        return session
    
    def get_session(self, session_id: str, user_id: str) -> Optional[ChatEntity]:
        """
        Busca sessão por ID
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão encontrada ou None
        """
        return self.chat_repository.get_session(session_id, user_id)
    
    def send_message(self, session_id: str, dto: ChatMessageRequest, user_id: str) -> ChatEntity:
        """
        Envia mensagem para o chat
        
        Args:
            session_id: ID da sessão
            dto: Dados da mensagem
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Mensagem enviada
        """
        # 1. Busca sessão
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Sessão não encontrada")
        
        # 2. Cria mensagem via Factory
        message = ChatFactory.create_message(dto, session_id, user_id)
        
        # 3. Persiste
        self.chat_repository.add_message(message)
        
        return message
    
    def get_chat_history(self, session_id: str, user_id: str, page: int = 1, size: int = 20) -> tuple[List[ChatEntity], int]:
        """
        Busca histórico de mensagens
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            page: Página
            size: Tamanho da página
            
        Returns:
            tuple: Lista de mensagens e total
        """
        return self.chat_repository.get_messages(session_id, user_id, page, size)
    
    def list_sessions(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> tuple[List[ChatEntity], int]:
        """
        Lista sessões do usuário
        
        Args:
            user_id: ID do usuário
            page: Página
            size: Tamanho da página
            status: Filtro por status
            
        Returns:
            tuple: Lista de sessões e total
        """
        return self.chat_repository.list_sessions(user_id, page, size, status)
    
    def close_session(self, session_id: str, user_id: str) -> ChatEntity:
        """
        Fecha sessão de chat
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão fechada
        """
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Sessão não encontrada")
        
        session.close()
        self.chat_repository.update_session(session)
        
        return session
