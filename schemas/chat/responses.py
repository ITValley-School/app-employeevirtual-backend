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

class ChatSessionResponse(BaseModel):
    """Response para sessão de chat"""
    id: str = Field(..., description="ID da sessão")
    title: str = Field(..., description="Título da sessão")
    user_id: str = Field(..., description="ID do usuário")
    status: str = Field(..., description="Status da sessão")
    created_at: datetime = Field(..., description="Data de criação")

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
    """Response para listagem de chats/sessões"""
    chats: List[ChatSessionResponse] = Field(..., description="Lista de sessões de chat")
    total: int = Field(..., description="Total de sessões")
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

class ChatHistoryResponse(BaseModel):
    """Response para histórico de mensagens"""
    messages: List['ChatHistoryMessageResponse'] = Field(..., description="Lista de mensagens")
    total: int = Field(..., description="Total de mensagens")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")

class ChatHistoryMessageResponse(BaseModel):
    """Response para mensagem no histórico (compatível com MongoDB)"""
    id: str = Field(..., description="UUID da mensagem")
    message: str = Field(..., description="Conteúdo da mensagem")
    sender: str = Field(..., description="Quem enviou (user ou assistant)")
    created_at: datetime = Field(..., description="Timestamp da mensagem")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados")

class ChatSendResponse(BaseModel):
    """Response para envio de mensagem (com resposta do assistente)"""
    message: str = Field(..., description="Mensagem enviada pelo usuário")
    response: str = Field(..., description="Resposta do assistente")
    message_id: str = Field(..., description="ID da mensagem do usuário")
    response_id: str = Field(..., description="ID da resposta do assistente")
    timestamp: datetime = Field(..., description="Timestamp da resposta")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")


class ConversationSidebarItem(BaseModel):
    """Item de conversa para exibir na sidebar"""
    id: str = Field(..., description="ID da conversa")
    title: str = Field(..., description="Título da conversa")
    agent_id: str = Field(..., description="ID do agente")
    user_id: str = Field(..., description="ID do usuário")
    message_count: int = Field(default=0, description="Número de mensagens")
    status: str = Field(default="active", description="Status da conversa")
    last_activity: datetime = Field(..., description="Última atividade")
    created_at: datetime = Field(..., description="Data de criação")


class AgentConversationsResponse(BaseModel):
    """Response para listagem de conversas de um agente na sidebar"""
    agent_id: str = Field(..., description="ID do agente")
    conversations: List[ConversationSidebarItem] = Field(..., description="Lista de conversas ativas")
    total: int = Field(..., description="Total de conversas")
