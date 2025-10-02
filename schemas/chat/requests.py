"""
Schemas de requisição para chat
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class ChatMessageType(str, Enum):
    """Tipos de mensagem"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatCreateRequest(BaseModel):
    """Request para criação de chat"""
    title: str = Field(..., min_length=2, max_length=100, description="Título do chat")
    agent_id: Optional[str] = Field(None, description="ID do agente associado")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto do chat")

class ChatMessageRequest(BaseModel):
    """Request para envio de mensagem"""
    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")

class ChatSessionRequest(BaseModel):
    """Request para criação de sessão de chat"""
    title: str = Field(..., min_length=2, max_length=100, description="Título da sessão")
    agent_id: Optional[str] = Field(None, description="ID do agente associado")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto da sessão")

class ChatUpdateRequest(BaseModel):
    """Request para atualização de chat"""
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    agent_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
