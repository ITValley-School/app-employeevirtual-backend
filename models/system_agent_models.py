"""
Models para Agentes do Sistema - Nova feature de catálogo IT Valley
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
import enum
import json

from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.uuid_models import UUIDColumn, generate_uuid, uuid_field, required_uuid_field
from data.base import Base

# Enums
class SystemAgentStatus(str, enum.Enum):
    """Status do agente do sistema"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class AgentStatus(str, enum.Enum):
    """Status do agente do sistema"""
    ACTIVE = "active"
    HIDDEN = "hidden"
    DEPRECATED = "deprecated"

class UserPlan(str, enum.Enum):
    """Planos de usuário"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

# =============================================
# TABELAS DO BANCO DE DADOS
# =============================================

class SystemAgentCategory(Base):
    """Tabela de categorias dos agentes do sistema"""
    __tablename__ = "system_agent_categories"
    
    id = UUIDColumn(primary_key=True, default=generate_uuid)
    name = Column(String(80), nullable=False, unique=True)
    icon = Column(String(50), nullable=True)
    description = Column(String(300), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SystemAgentCategory(id={self.id}, name='{self.name}')>"

class SystemAgent(Base):
    """Tabela principal dos agentes do sistema"""
    __tablename__ = "system_agents"
    
    id = UUIDColumn(primary_key=True, default=generate_uuid)
    
    # Identificação
    name = Column(String(120), nullable=False)
    short_description = Column(String(500), nullable=False)
    category_id = UUIDColumn(ForeignKey("system_agent_categories.id"), nullable=False)
    icon = Column(String(50), nullable=True)
    
    # Status
    status = Column(SQLEnum(SystemAgentStatus), nullable=False, default=SystemAgentStatus.ACTIVE)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamentos
    category = relationship("SystemAgentCategory", backref="agents")
    
    def __repr__(self):
        return f"<SystemAgent(id={self.id}, name='{self.name}')>"

class SystemAgentVersion(Base):
    """Tabela de versões dos agentes do sistema"""
    __tablename__ = "system_agent_versions"
    
    id = UUIDColumn(primary_key=True, default=generate_uuid)
    
    # Referência ao agente
    system_agent_id = UUIDColumn(ForeignKey("system_agents.id"), nullable=False)
    
    # Versionamento
    version = Column(String(20), nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    status = Column(SQLEnum(AgentStatus), nullable=False, default=AgentStatus.ACTIVE)
    
    # Schemas JSON
    input_schema = Column(Text, nullable=False)  # JSON Schema
    output_schema = Column(Text, nullable=False)  # JSON Schema
    
    # Integração com Orion
    orion_workflows = Column(Text, nullable=False)  # JSON array de workflow names
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamentos
    system_agent = relationship("SystemAgent", backref="versions")
    
    @property
    def input_schema_data(self) -> Dict[str, Any]:
        """Converte input schema JSON para dict"""
        try:
            return json.loads(self.input_schema)
        except json.JSONDecodeError:
            return {}
    
    @input_schema_data.setter
    def input_schema_data(self, value: Dict[str, Any]):
        """Converte dict para JSON"""
        self.input_schema = json.dumps(value)
    
    @property
    def output_schema_data(self) -> Dict[str, Any]:
        """Converte output schema JSON para dict"""
        try:
            return json.loads(self.output_schema)
        except json.JSONDecodeError:
            return {}
    
    @output_schema_data.setter
    def output_schema_data(self, value: Dict[str, Any]):
        """Converte dict para JSON"""
        self.output_schema = json.dumps(value)
    
    @property
    def orion_workflow_list(self) -> List[str]:
        """Converte workflows JSON para lista"""
        try:
            return json.loads(self.orion_workflows)
        except json.JSONDecodeError:
            return []
    
    @orion_workflow_list.setter
    def orion_workflow_list(self, value: List[str]):
        """Converte lista para JSON"""
        self.orion_workflows = json.dumps(value)
    
    def __repr__(self):
        return f"<SystemAgentVersion(id={self.id}, version='{self.version}')>"

class SystemAgentVisibility(Base):
    """Tabela de regras de visibilidade dos agentes do sistema"""
    __tablename__ = "system_agent_visibility"
    
    id = UUIDColumn(primary_key=True, default=generate_uuid)
    
    # Referência ao agente
    system_agent_id = UUIDColumn(ForeignKey("system_agents.id"), nullable=False)
    
    # Regras de visibilidade
    tenant_id = Column(String(50), nullable=True)  # null = todos os tenants
    plan = Column(SQLEnum(UserPlan), nullable=True)  # null = todos os planos
    region = Column(String(30), nullable=True)  # null = todas as regiões
    is_visible = Column(Boolean, nullable=False, default=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamentos
    system_agent = relationship("SystemAgent", backref="visibility_rules")
    
    def __repr__(self):
        return f"<SystemAgentVisibility(id={self.id}, tenant='{self.tenant_id}', plan='{self.plan}')>"

# =============================================
# DTOs DE REQUEST/RESPONSE PARA AS APIS
# =============================================

# Category DTOs
class CategoryResponse(BaseModel):
    """Response com dados da categoria"""
    id: UUID
    name: str
    icon: Optional[str]
    description: Optional[str]
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CreateCategoryRequest(BaseModel):
    """Request para criar categoria"""
    name: str = Field(..., max_length=80, description="Nome da categoria")
    icon: Optional[str] = Field(None, max_length=50, description="Ícone da categoria")
    description: Optional[str] = Field(None, max_length=300, description="Descrição da categoria")
    order_index: int = Field(0, description="Ordem de exibição")

class UpdateCategoryRequest(BaseModel):
    """Request para atualizar categoria"""
    name: Optional[str] = Field(None, max_length=80, description="Nome da categoria")
    icon: Optional[str] = Field(None, max_length=50, description="Ícone da categoria")
    description: Optional[str] = Field(None, max_length=300, description="Descrição da categoria")
    order_index: Optional[int] = Field(None, description="Ordem de exibição")
    is_active: Optional[bool] = Field(None, description="Se a categoria está ativa")

# Agent DTOs
class AgentVersionResponse(BaseModel):
    """Response com dados da versão do agente"""
    id: UUID
    version: str
    is_default: bool
    status: AgentStatus
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    orion_workflows: List[str]
    created_at: datetime
    updated_at: datetime

class AgentVisibilityResponse(BaseModel):
    """Response com dados da regra de visibilidade"""
    id: UUID
    tenant_id: Optional[str]
    plan: Optional[UserPlan]
    region: Optional[str]
    is_visible: bool
    created_at: datetime
    updated_at: datetime

class SystemAgentResponse(BaseModel):
    """Response com dados completos do agente"""
    id: UUID
    name: str
    short_description: str
    category_id: UUID
    icon: Optional[str]
    status: SystemAgentStatus
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse
    versions: List[AgentVersionResponse]
    visibility_rules: List[AgentVisibilityResponse]

class SystemAgentSummaryResponse(BaseModel):
    """Response resumido do agente para listagens"""
    id: UUID
    name: str
    short_description: str
    category_id: UUID
    icon: Optional[str]
    status: SystemAgentStatus
    default_version: Optional[str]

# User DTOs
class UserSystemAgentResponse(BaseModel):
    """Response de agente para usuários finais"""
    id: UUID
    name: str
    short_description: str
    category_id: UUID
    icon: Optional[str]
    default_version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

class UserCategoryWithAgentsResponse(BaseModel):
    """Response de categoria com agentes para usuários"""
    id: UUID
    name: str
    icon: Optional[str]
    description: Optional[str]
    order_index: int
    agents: List[UserSystemAgentResponse]

# Admin DTOs
class CreateSystemAgentRequest(BaseModel):
    """Request para criar agente do sistema"""
    name: str = Field(..., max_length=120, description="Nome do agente")
    short_description: str = Field(..., max_length=500, description="Descrição curta")
    category_id: UUID = required_uuid_field(description="ID da categoria")
    icon: Optional[str] = Field(None, max_length=50, description="Ícone do agente")

class UpdateSystemAgentRequest(BaseModel):
    """Request para atualizar agente do sistema"""
    name: Optional[str] = Field(None, max_length=120, description="Nome do agente")
    short_description: Optional[str] = Field(None, max_length=500, description="Descrição curta")
    category_id: Optional[UUID] = uuid_field(description="ID da categoria")
    icon: Optional[str] = Field(None, max_length=50, description="Ícone do agente")
    status: Optional[SystemAgentStatus] = Field(None, description="Status do agente")

class CreateSystemAgentVersionRequest(BaseModel):
    """Request para criar versão do agente"""
    version: str = Field(..., max_length=20, description="Número da versão")
    input_schema: Dict[str, Any] = Field(..., description="Schema JSON de input")
    output_schema: Dict[str, Any] = Field(..., description="Schema JSON de output")
    orion_workflows: List[str] = Field(..., description="Lista de workflows do Orion")
    is_default: bool = Field(False, description="Versão padrão")

class UpdateSystemAgentVersionRequest(BaseModel):
    """Request para atualizar versão do agente"""
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Schema JSON de input")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Schema JSON de output")
    orion_workflows: Optional[List[str]] = Field(None, description="Lista de workflows do Orion")
    is_default: Optional[bool] = Field(None, description="Versão padrão")
    status: Optional[AgentStatus] = Field(None, description="Status da versão")

class CreateSystemAgentVisibilityRequest(BaseModel):
    """Request para criar regra de visibilidade"""
    tenant_id: Optional[str] = Field(None, max_length=50, description="ID do tenant")
    plan: Optional[UserPlan] = Field(None, description="Plano de usuário")
    region: Optional[str] = Field(None, max_length=30, description="Região")
    is_visible: bool = Field(True, description="Se é visível")

class UpdateSystemAgentVisibilityRequest(BaseModel):
    """Request para atualizar regra de visibilidade"""
    tenant_id: Optional[str] = Field(None, max_length=50, description="ID do tenant")
    plan: Optional[UserPlan] = Field(None, description="Plano de usuário")
    region: Optional[str] = Field(None, max_length=30, description="Região")
    is_visible: Optional[bool] = Field(None, description="Se é visível")
