"""
Modelos de dados para agentes do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Enum as SQLEnum, ForeignKey, text
from sqlalchemy.sql import func
from models.uuid_models import UUIDColumn
from data.base import Base


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

# Modelos Pydantic (para API)
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
    
# Modelos SQLAlchemy (para banco de dados)
class Agent(Base):
    """Tabela de agentes"""
    __tablename__ = "agents"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), default=AgentType.CUSTOM, nullable=False)
    system_prompt = Column(Text, nullable=False)
    personality = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    status = Column(String(20), default=AgentStatus.ACTIVE, nullable=False)
    llm_provider = Column(String(50), default=LLMProvider.OPENAI, nullable=False)
    model = Column(String(100), nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.agent_type}')>"

class AgentKnowledge(Base):
    """Tabela de base de conhecimento dos agentes"""
    __tablename__ = "agent_knowledge"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    agent_id = Column(UUIDColumn, ForeignKey('empl.agents.id'), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_url = Column(String(500), nullable=False)
    orion_file_id = Column(String(100), nullable=True)  # ID do arquivo no Orion
    processed = Column(Boolean, default=False, nullable=False)
    vector_ids = Column(Text, nullable=True)  # JSON array de IDs dos vetores no Pinecone
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<AgentKnowledge(id={self.id}, agent_id={self.agent_id}, file='{self.file_name}')>"

class AgentExecutionDB(Base):
    """Tabela de execuções de agentes"""
    __tablename__ = "agent_executions"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    agent_id = Column(UUIDColumn, ForeignKey('empl.agents.id'), nullable=False, index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    execution_time = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    context = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AgentExecutionDB(id={self.id}, agent_id={self.agent_id}, success={self.success})>"

class LegacySystemAgent(Base):
    """Tabela de agentes do sistema (pré-configurados) - LEGACY"""
    __tablename__ = "legacy_system_agents"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    agent_type = Column(String(50), nullable=False)
    system_prompt = Column(Text, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    orion_endpoint = Column(String(200), nullable=True)  # Endpoint específico no Orion
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<LegacySystemAgent(id={self.id}, name='{self.name}', type='{self.agent_type}')>"

