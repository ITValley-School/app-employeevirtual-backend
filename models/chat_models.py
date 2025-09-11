"""
Modelos de domínio para chat/conversação do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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

