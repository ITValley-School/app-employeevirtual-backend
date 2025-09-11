"""
Modelos de dados para chat/conversação do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, text
from sqlalchemy.sql import func
from data.base import Base
from models.uuid_models import UUIDColumn


class MessageType(str, Enum):
    """Tipos de mensagem"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class ConversationStatus(str, Enum):
    """Status da conversação"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

# Modelos Pydantic (para API)
class MessageBase(BaseModel):
    """Modelo base de mensagem"""
    content: str = Field(..., min_length=1, description="Conteúdo da mensagem")
    message_type: MessageType = Field(..., description="Tipo da mensagem")
    
class MessageCreate(MessageBase):
    """Modelo para criação de mensagem"""
    conversation_id: str = Field(..., description="ID da conversação")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados da mensagem")
    
class MessageResponse(MessageBase):
    """Modelo de resposta da mensagem"""
    id: str
    conversation_id: str
    user_id: str
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    edited_at: Optional[datetime] = None
    is_edited: bool = False
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    """Modelo base da conversação"""
    title: Optional[str] = Field(None, max_length=200, description="Título da conversação")
    
class ConversationCreate(ConversationBase):
    """Modelo para criação de conversação"""
    agent_id: str = Field(..., description="ID do agente")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto adicional da conversação")
    
class ConversationUpdate(BaseModel):
    """Modelo para atualização de conversação"""
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[ConversationStatus] = None
    
class ConversationResponse(ConversationBase):
    """Modelo de resposta da conversação"""
    id: str
    user_id: str
    agent_id: str
    agent_name: str
    status: ConversationStatus
    message_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationResponse):
    """Conversação com mensagens"""
    messages: List[MessageResponse] = []

class ChatRequest(BaseModel):
    """Solicitação de chat"""
    agent_id: str = Field(..., description="ID do agente")
    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    conversation_id: Optional[str] = Field(None, description="ID da conversação (opcional para nova conversa)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto adicional")
    
class ChatResponse(BaseModel):
    """Resposta do chat"""
    conversation_id: str
    user_message: MessageResponse
    agent_response: MessageResponse
    agent_name: str
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None
    
class ConversationSummary(BaseModel):
    """Resumo da conversação"""
    id: str
    title: str
    agent_name: str
    message_count: int
    last_message_preview: str
    last_message_at: datetime
    created_at: datetime

# Modelos SQLAlchemy (para banco de dados)
class Conversation(Base):
    """Tabela de conversações"""
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
        return f"<Conversation(id={self.id}, user_id={self.user_id}, agent_id={self.agent_id})>"

class Message(Base):
    """Tabela de mensagens"""
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
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, type='{self.message_type}')>"

class ConversationContext(Base):
    """Tabela de contexto das conversações"""
    __tablename__ = "conversation_contexts"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    conversation_id = Column(UUIDColumn, ForeignKey('empl.conversations.id'), nullable=False, index=True)
    context_key = Column(String(100), nullable=False)
    context_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConversationContext(id={self.id}, conversation_id={self.conversation_id}, key='{self.context_key}')>"

class MessageReaction(Base):
    """Tabela de reações às mensagens"""
    __tablename__ = "message_reactions"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    message_id = Column(UUIDColumn, ForeignKey('empl.messages.id'), nullable=False, index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    reaction_type = Column(String(20), nullable=False)  # like, dislike, helpful, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MessageReaction(id={self.id}, message_id={self.message_id}, type='{self.reaction_type}')>"

