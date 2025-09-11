"""
Entidades SQLAlchemy para chat/conversação do sistema EmployeeVirtual
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, text
from sqlalchemy.sql import func

from models.uuid_models import UUIDColumn
from data.base import Base
from models.chat_models import MessageType, ConversationStatus


class ConversationEntity(Base):
    """Entidade de conversações"""
    __tablename__ = "conversations"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    agent_id = Column(UUIDColumn, ForeignKey('empl.agents.id'), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ConversationEntity(id={self.id}, user_id={self.user_id}, agent_id={self.agent_id})>"


class MessageEntity(Base):
    """Entidade de mensagens"""
    __tablename__ = "messages"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    conversation_id = Column(UUIDColumn, ForeignKey('empl.conversations.id'), nullable=False, index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    agent_id = Column(UUIDColumn, ForeignKey('empl.agents.id'), nullable=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), nullable=False)
    message_metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_edited = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<MessageEntity(id={self.id}, conversation_id={self.conversation_id}, type='{self.message_type}')>"


class ConversationContextEntity(Base):
    """Entidade de contexto das conversações"""
    __tablename__ = "conversation_contexts"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    conversation_id = Column(UUIDColumn, ForeignKey('empl.conversations.id'), nullable=False, index=True)
    context_key = Column(String(100), nullable=False)
    context_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConversationContextEntity(id={self.id}, conversation_id={self.conversation_id}, key='{self.context_key}')>"


class MessageReactionEntity(Base):
    """Entidade de reações às mensagens"""
    __tablename__ = "message_reactions"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    message_id = Column(UUIDColumn, ForeignKey('empl.messages.id'), nullable=False, index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    reaction_type = Column(String(20), nullable=False)  # like, dislike, helpful, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MessageReactionEntity(id={self.id}, message_id={self.message_id}, type='{self.reaction_type}')>"
