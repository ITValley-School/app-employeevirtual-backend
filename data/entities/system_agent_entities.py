"""
Entidades de Agentes de Sistema - EmployeeVirtual
Seguindo padrão IT Valley Architecture
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func

from data.base import Base

# Configuração de schema baseada no tipo de banco
USE_SCHEMA = True  # Usar schema para Azure SQL
SCHEMA_CONFIG = {'schema': 'empl'} if USE_SCHEMA else {}


class SystemAgentEntity(Base):
    """Entidade de agentes de sistema"""
    __tablename__ = "system_agents"
    __table_args__ = SCHEMA_CONFIG

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    agent_type = Column(String(50), nullable=False)
    system_prompt = Column(String(2000), nullable=False)
    avatar_url = Column(String(500))
    orion_endpoint = Column(String(500))  # Endpoint específico do Orion para este agente
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SystemAgentEntity(id={self.id}, name='{self.name}', type='{self.agent_type}')>"

    def activate(self) -> None:
        """Ativa o agente de sistema"""
        self.is_active = True

    def deactivate(self) -> None:
        """Desativa o agente de sistema"""
        self.is_active = False

