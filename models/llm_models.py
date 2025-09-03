"""
Modelos para gerenciamento de chaves LLM
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, Text, DECIMAL, ForeignKey, text
from sqlalchemy.sql import func
from models.uuid_models import UUIDColumn
from data.base import Base

# Enums
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

class KeyStatus(str, Enum):
    """Status das chaves LLM"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

# Modelos Pydantic (para API)
class LLMKeyBase(BaseModel):
    """Modelo base para chaves LLM"""
    provider: LLMProvider = Field(..., description="Provedor do LLM")
    usage_limit: Optional[float] = Field(None, ge=0, description="Limite de uso mensal")
    is_active: bool = Field(default=True, description="Chave ativa")

class SystemLLMKeyCreate(LLMKeyBase):
    """Modelo para criação de chave LLM do sistema"""
    api_key: str = Field(..., min_length=10, description="Chave API do provedor")

class SystemLLMKeyUpdate(BaseModel):
    """Modelo para atualização de chave LLM do sistema"""
    api_key: Optional[str] = Field(None, min_length=10)
    usage_limit: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

class SystemLLMKeyResponse(LLMKeyBase):
    """Modelo de resposta para chave LLM do sistema"""
    id: str = Field(..., description="UUID único da chave")
    current_usage: float = Field(default=0, description="Uso atual no mês")
    last_used: Optional[datetime] = Field(None, description="Última vez que foi usada")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    
    class Config:
        from_attributes = True

class UserLLMKeyCreate(LLMKeyBase):
    """Modelo para criação de chave LLM do usuário"""
    api_key: str = Field(..., min_length=10, description="Chave API do provedor")

class UserLLMKeyUpdate(BaseModel):
    """Modelo para atualização de chave LLM do usuário"""
    api_key: Optional[str] = Field(None, min_length=10)
    usage_limit: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

class UserLLMKeyResponse(LLMKeyBase):
    """Modelo de resposta para chave LLM do usuário"""
    id: str = Field(..., description="UUID único da chave")
    user_id: str = Field(..., description="UUID do usuário proprietário")
    current_usage: float = Field(default=0, description="Uso atual no mês")
    last_used: Optional[datetime] = Field(None, description="Última vez que foi usada")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    
    class Config:
        from_attributes = True

class LLMKeyValidationRequest(BaseModel):
    """Modelo para validação de chave LLM"""
    provider: LLMProvider = Field(..., description="Provedor do LLM")
    api_key: str = Field(..., min_length=10, description="Chave API para validar")

class LLMKeyValidationResponse(BaseModel):
    """Modelo de resposta para validação de chave LLM"""
    is_valid: bool = Field(..., description="Chave é válida")
    provider: LLMProvider = Field(..., description="Provedor validado")
    message: str = Field(..., description="Mensagem de validação")
    model_info: Optional[dict] = Field(None, description="Informações do modelo")

class LLMKeyUsageStats(BaseModel):
    """Modelo para estatísticas de uso das chaves"""
    provider: LLMProvider = Field(..., description="Provedor do LLM")
    total_usage: float = Field(..., description="Uso total no mês")
    usage_limit: Optional[float] = Field(None, description="Limite de uso")
    usage_percentage: float = Field(..., description="Percentual de uso")
    last_used: Optional[datetime] = Field(None, description="Última utilização")

# Modelos SQLAlchemy (para banco de dados)
class SystemLLMKey(Base):
    """Tabela de chaves LLM do sistema"""
    __tablename__ = "system_llm_keys"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"))
    provider = Column(String(50), nullable=False, index=True)
    api_key = Column(String(500), nullable=False)  # chave criptografada
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    usage_limit = Column(DECIMAL(10,2), nullable=True)
    current_usage = Column(DECIMAL(10,2), default=0, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemLLMKey(id={self.id}, provider='{self.provider}', active={self.is_active})>"

class UserLLMKey(Base):
    """Tabela de chaves LLM dos usuários"""
    __tablename__ = "user_llm_keys"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"))
    user_id = Column(UUIDColumn, ForeignKey('empl.users.id'), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    api_key = Column(String(500), nullable=False)  # chave criptografada
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    usage_limit = Column(DECIMAL(10,2), nullable=True)
    current_usage = Column(DECIMAL(10,2), default=0, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserLLMKey(id={self.id}, user_id={self.user_id}, provider='{self.provider}')>"

# Configuração do schema
SCHEMA_CONFIG = {'schema': 'empl'}
