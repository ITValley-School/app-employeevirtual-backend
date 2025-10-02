"""
Schemas de resposta para chat
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ChatMessageType(str, Enum):
    """Tipos de mensagem"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatResponse(BaseModel):
    """Response básico do chat"""
    id: str = Field(..., description="UUID único do chat")
    title: str = Field(..., description="Título do chat")
    agent_id: Optional[str] = Field(None, description="ID do agente associado")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de última atualização")
    user_id: str = Field(..., description="ID do usuário proprietário")

class ChatDetailResponse(ChatResponse):
    """Response detalhado do chat"""
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto do chat")
    total_messages: int = Field(default=0, description="Total de mensagens")
    last_message: Optional[datetime] = Field(None, description="Última mensagem")

class ChatListResponse(BaseModel):
    """Response para listagem de chats"""
    chats: List[ChatResponse] = Field(..., description="Lista de chats")
    total: int = Field(..., description="Total de chats")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")

class ChatMessageResponse(BaseModel):
    """Response para mensagem do chat"""
    id: str = Field(..., description="UUID da mensagem")
    chat_id: str = Field(..., description="ID do chat")
    type: ChatMessageType = Field(..., description="Tipo da mensagem")
    content: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime = Field(..., description="Timestamp da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados da mensagem")

class ChatSendResponse(BaseModel):
    """Response para envio de mensagem"""
    chat_id: str = Field(..., description="ID do chat")
    message: ChatMessageResponse = Field(..., description="Mensagem enviada")
    response: Optional[ChatMessageResponse] = Field(None, description="Resposta do assistente")
    execution_time: float = Field(..., description="Tempo de execução em segundos")
