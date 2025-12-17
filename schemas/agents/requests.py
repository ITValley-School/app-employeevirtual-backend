"""
Schemas de requisição para agentes
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class AgentStatus(str, Enum):
    """Status do agente"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    ERROR = "error"

class AgentType(str, Enum):
    """Tipos de agente"""
    CHATBOT = "chatbot"
    ASSISTANT = "assistant"
    AUTOMATION = "automation"
    ANALYZER = "analyzer"

class AgentCreateRequest(BaseModel):
    """Request para criação de agente"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do agente")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do agente")
    type: AgentType = Field(..., description="Tipo do agente")
    instructions: str = Field(..., min_length=3, description="Instruções para o agente")
    model: Optional[str] = Field(None, description="Modelo de IA")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperatura do modelo")
    max_tokens: Optional[int] = Field(None, ge=100, le=4000, description="Máximo de tokens")
    system_prompt: Optional[str] = Field(None, description="Prompt do sistema")

class AgentUpdateRequest(BaseModel):
    """Request para atualização de agente"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    instructions: Optional[str] = Field(None, min_length=3)
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=4000)
    system_prompt: Optional[str] = None
    status: Optional[AgentStatus] = None

class AgentExecuteRequest(BaseModel):
    """Request para execução de agente"""
    message: str = Field(..., min_length=1, description="Mensagem para o agente")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    session_id: Optional[str] = Field(None, description="ID da sessão")

class AgentTrainRequest(BaseModel):
    """Request para treinamento de agente"""
    training_data: List[Dict[str, str]] = Field(..., description="Dados de treinamento")
    epochs: int = Field(default=10, ge=1, le=100, description="Número de épocas")
    learning_rate: float = Field(default=0.001, ge=0.0001, le=0.1, description="Taxa de aprendizado")

class AgentDocumentMetadataUpdateRequest(BaseModel):
    """Request para atualização de metadados de documento"""
    metadata: Dict[str, Any] = Field(..., description="Metadados a serem atualizados")
