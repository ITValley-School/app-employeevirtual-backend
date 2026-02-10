"""
Repository para chat
Persistência de dados seguindo padrão IT Valley Architecture
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from domain.chat.chat_entity import ChatEntity
from data.entities.chat_entities import ChatSessionEntity, ChatMessageEntity


class ChatRepository:
    """Repository para persistência de chat"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_session(self, session: ChatEntity) -> ChatEntity:
        """
        Adiciona sessão no banco de dados
        
        Args:
            session: Sessão para adicionar
            
        Returns:
            ChatEntity: Sessão adicionada
        """
        # Cria entidade de banco
        db_session = ChatSessionEntity(
            id=session.id,
            user_id=session.user_id,
            agent_id=session.agent_id,
            title=session.title,
            status=session.status,
            created_at=session.created_at
        )
        
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        return session
    
    def add_message(self, message: ChatEntity) -> ChatEntity:
        """
        Adiciona mensagem no banco de dados
        
        Args:
            message: Mensagem para adicionar
            
        Returns:
            ChatEntity: Mensagem adicionada
        """
        import json
        
        # Cria entidade de banco
        db_message = ChatMessageEntity(
            id=message.id,
            session_id=message.session_id,
            user_id=message.user_id,
            message=message.message,
            sender=message.sender,
            context=json.dumps(message.context) if message.context else None,  # Converter dict para JSON string
            created_at=message.created_at
        )
        
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        return message
    
    def get_session(self, session_id: str, user_id: str) -> Optional[ChatEntity]:
        """
        Busca sessão por ID
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão encontrada ou None
        """
        db_session = self.db.query(ChatSessionEntity).filter(
            and_(
                ChatSessionEntity.id == session_id,
                ChatSessionEntity.user_id == user_id
            )
        ).first()
        
        if not db_session:
            return None
        
        # Converte para domain entity
        from domain.chat.chat_entity import ChatEntity
        return ChatEntity(
            id=db_session.id,
            user_id=db_session.user_id,
            agent_id=db_session.agent_id,
            title=db_session.title,
            status=db_session.status,
            created_at=db_session.created_at
        )
    
    def get_active_session_by_agent(self, agent_id: str, user_id: str) -> Optional[ChatEntity]:
        """
        Busca sessão ativa por agente e usuário
        
        Retorna a sessão mais recente ativa para o agente e usuário especificados.
        Isso permite reutilizar a mesma conversa ao invés de criar uma nova a cada mensagem.
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão ativa encontrada ou None
        """
        db_session = self.db.query(ChatSessionEntity).filter(
            and_(
                ChatSessionEntity.agent_id == agent_id,
                ChatSessionEntity.user_id == user_id,
                ChatSessionEntity.status == "active"
            )
        ).order_by(ChatSessionEntity.created_at.desc()).first()
        
        if not db_session:
            return None
        
        # Converte para domain entity
        from domain.chat.chat_entity import ChatEntity
        return ChatEntity(
            id=db_session.id,
            user_id=db_session.user_id,
            agent_id=db_session.agent_id,
            title=db_session.title,
            status=db_session.status,
            created_at=db_session.created_at
        )
    
    def update_session(self, session: ChatEntity) -> ChatEntity:
        """
        Atualiza sessão no banco de dados
        
        Args:
            session: Sessão para atualizar
            
        Returns:
            ChatEntity: Sessão atualizada
        """
        db_session = self.db.query(ChatSessionEntity).filter(
            ChatSessionEntity.id == session.id
        ).first()
        
        if db_session:
            db_session.title = session.title
            db_session.status = session.status
            db_session.closed_at = session.closed_at if hasattr(session, 'closed_at') else None
            
            self.db.commit()
            self.db.refresh(db_session)
        
        return session
    
    def get_messages(self, session_id: str, user_id: str, page: int = 1, size: int = 20) -> tuple[List[ChatEntity], int]:
        """
        Busca mensagens da sessão
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            page: Página
            size: Tamanho da página
            
        Returns:
            tuple: Lista de mensagens e total
        """
        # Verifica se sessão pertence ao usuário
        session = self.db.query(ChatSessionEntity).filter(
            and_(
                ChatSessionEntity.id == session_id,
                ChatSessionEntity.user_id == user_id
            )
        ).first()
        
        if not session:
            return [], 0
        
        # Busca mensagens com paginação
        query = self.db.query(ChatMessageEntity).filter(
            ChatMessageEntity.session_id == session_id
        ).order_by(ChatMessageEntity.created_at.desc())
        
        total = query.count()
        
        offset = (page - 1) * size
        db_messages = query.offset(offset).limit(size).all()
        
        # Converte para domain entities
        from domain.chat.chat_entity import ChatEntity
        messages = [
            ChatEntity(
                id=msg.id,
                session_id=msg.session_id,
                user_id=msg.user_id,
                message=msg.message,
                sender=msg.sender,
                context=msg.context,
                created_at=msg.created_at
            )
            for msg in db_messages
        ]
        
        return messages, total
    
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
        query = self.db.query(ChatSessionEntity).filter(
            ChatSessionEntity.user_id == user_id
        )
        
        if status:
            query = query.filter(ChatSessionEntity.status == status)
        
        query = query.order_by(ChatSessionEntity.created_at.desc())
        
        total = query.count()
        
        offset = (page - 1) * size
        db_sessions = query.offset(offset).limit(size).all()
        
        # Converte para domain entities
        from domain.chat.chat_entity import ChatEntity
        sessions = [
            ChatEntity(
                id=s.id,
                user_id=s.user_id,
                agent_id=s.agent_id,
                title=s.title,
                status=s.status,
                created_at=s.created_at
            )
            for s in db_sessions
        ]
        
        return sessions, total
