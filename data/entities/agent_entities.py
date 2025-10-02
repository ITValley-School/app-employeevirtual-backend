"""
Entidades de Agentes - EmployeeVirtual
Seguindo padrão IT Valley Architecture
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum, text
from sqlalchemy.sql import func
from enum import Enum
from typing import Any

from data.base import Base

# Enums locais
class AgentStatus(str, Enum):
    """Status do agente"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"

class AgentType(str, Enum):
    """Tipos de agente"""
    CHATBOT = "chatbot"
    ASSISTANT = "assistant"
    AUTOMATION = "automation"
    ANALYTICS = "analytics"

# Configuração de schema baseada no tipo de banco
USE_SCHEMA = True  # Usar schema para Azure SQL
SCHEMA_CONFIG = {'schema': 'empl'} if USE_SCHEMA else {}

class AgentEntity(Base):
    """Entidade de agentes"""
    __tablename__ = "agents"
    __table_args__ = SCHEMA_CONFIG

    id = Column(String(32), primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(String(32), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(SQLEnum(AgentType), default=AgentType.CHATBOT, nullable=False)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.DRAFT, nullable=False)
    configuration = Column(Text)  # JSON com configurações
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_execution = Column(DateTime(timezone=True))
    execution_count = Column(Text, default="0")
    is_public = Column(Boolean, default=False)
    tags = Column(Text)  # JSON com tags

    def __repr__(self):
        return f"<AgentEntity(id={self.id}, name='{self.name}', type='{self.type}')>"

    def activate(self) -> None:
        """Ativa o agente"""
        self.status = AgentStatus.ACTIVE

    def deactivate(self) -> None:
        """Desativa o agente"""
        self.status = AgentStatus.INACTIVE

    def archive(self) -> None:
        """Arquiva o agente"""
        self.status = AgentStatus.ARCHIVED

    def apply_update_from_any(self, data: Any) -> None:
        """Aplica atualizações de forma segura"""
        # Lógica para aplicar atualizações de forma segura
        pass

class AgentExecutionEntity(Base):
    """Entidade de execuções de agentes"""
    __tablename__ = "agent_executions"
    __table_args__ = SCHEMA_CONFIG

    id = Column(String(32), primary_key=True, server_default=text("NEWID()"), index=True)
    agent_id = Column(String(32), nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    input_data = Column(Text)  # JSON com dados de entrada
    output_data = Column(Text)  # JSON com dados de saída
    execution_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    duration_ms = Column(Text, default="0")
    tokens_used = Column(Text, default="0")
    cost = Column(Text, default="0.00")
    status = Column(String(20), default="completed")  # completed, failed, timeout
    error_message = Column(Text)

    def __repr__(self):
        return f"<AgentExecutionEntity(id={self.id}, agent_id={self.agent_id})>"

class AgentVersionEntity(Base):
    """Entidade de versões de agentes"""
    __tablename__ = "agent_versions"
    __table_args__ = SCHEMA_CONFIG

    id = Column(String(32), primary_key=True, server_default=text("NEWID()"), index=True)
    agent_id = Column(String(32), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    configuration = Column(Text)  # JSON com configurações da versão
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=False)
    notes = Column(Text)

    def __repr__(self):
        return f"<AgentVersionEntity(id={self.id}, agent_id={self.agent_id}, version='{self.version}')>"
