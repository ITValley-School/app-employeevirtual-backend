"""
Modelos de domínio para agentes do sistema EmployeeVirtual
Responsabilidade: Definir contratos e estruturas de dados de negócio (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Tipos de agentes"""
    CUSTOM = "custom"           # Agente personalizado do usuário
    SYSTEM = "system"           # Agente do sistema (pré-configurado)
    TRANSCRIBER = "transcriber" # Transcrição de áudio
    YOUTUBE_TRANSCRIBER = "youtube_transcriber"
    PDF_READER = "pdf_reader"
    IMAGE_OCR = "image_ocr"


class AgentStatus(str, Enum):
    """Status do agente"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ERROR = "error"


class LLMProvider(str, Enum):
    """Provedores de LLM suportados"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    OLLAMA = "ollama"
    MISTRAL = "mistral"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"
    AZURE = "azure"
    OPENROUTER = "openrouter"


class AgentBase(BaseModel):
    """Modelo base do agente"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do agente")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do agente")
    agent_type: AgentType = Field(default=AgentType.CUSTOM, description="Tipo do agente")
    system_prompt: str = Field(..., min_length=10, description="Prompt do sistema")
    personality: Optional[str] = Field(None, description="Personalidade do agente")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")
    

class AgentCreate(AgentBase):
    """Modelo para criação de agente"""
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="Provedor do LLM")
    model: str = Field(..., description="Modelo específico")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Temperatura do modelo")
    max_tokens: Optional[int] = Field(default=None, description="Máximo de tokens")
    

class AgentUpdate(BaseModel):
    """Modelo para atualização de agente"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    system_prompt: Optional[str] = Field(None, min_length=10)
    personality: Optional[str] = None
    avatar_url: Optional[str] = None
    status: Optional[AgentStatus] = None
    llm_provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    

class AgentResponse(AgentBase):
    """Modelo de resposta do agente"""
    id: str  # UUID string
    user_id: str  # UUID string
    status: AgentStatus
    llm_provider: LLMProvider
    model: str
    temperature: float
    max_tokens: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int = 0
    
    class Config:
        from_attributes = True


class AgentExecutionRequest(BaseModel):
    """Modelo para requisição de execução de agente"""
    user_message: str = Field(..., min_length=1, description="Mensagem do usuário")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto adicional")
    

class AgentExecutionResponse(BaseModel):
    """Modelo de resposta da execução"""
    agent_id: str  # UUID string
    agent_name: str
    user_message: str
    response: str
    model_used: str
    execution_time: Optional[float]
    tokens_used: Optional[int]
    success: bool
    error_message: Optional[str] = None
    created_at: datetime
    

class AgentKnowledgeBase(BaseModel):
    """Modelo para base de conhecimento do agente"""
    agent_id: str  # UUID string
    file_name: str
    file_type: str
    file_size: int
    file_url: str
    processed: bool = False
    vector_ids: Optional[List[str]] = []


# Re-exportar entidades com nomes de compatibilidade
from data.entities.agent_entities import (
    AgentEntity as Agent,
    AgentKnowledgeEntity as AgentKnowledge,
    AgentExecutionEntity as AgentExecutionDB
    # SystemAgent já está definido em system_agent_models.py
)

