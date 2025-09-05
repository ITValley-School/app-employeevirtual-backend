"""
Modelos de dados para flows/automações do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Enum as SQLEnum, ForeignKey, JSON, text
from sqlalchemy.sql import func
from data.base import Base
from models.uuid_models import UUIDColumn


class FlowStatus(str, Enum):
    """Status do flow"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    PAUSED = "paused"
    ERROR = "error"

class ExecutionStatus(str, Enum):
    """Status da execução"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class StepType(str, Enum):
    """Tipos de etapas do flow"""
    AGENT_EXECUTION = "agent_execution"
    PAUSE_FOR_REVIEW = "pause_for_review"
    CONDITION = "condition"
    FILE_UPLOAD = "file_upload"
    ORION_SERVICE = "orion_service"

# Modelos Pydantic (para API)
class FlowStepBase(BaseModel):
    """Modelo base de uma etapa do flow"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome da etapa")
    step_type: StepType = Field(..., description="Tipo da etapa")
    order: int = Field(..., ge=1, description="Ordem de execução")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da etapa")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configurações específicas da etapa")
    
class FlowStepCreate(FlowStepBase):
    """Modelo para criação de etapa"""
    pass
    
class FlowStepUpdate(BaseModel):
    """Modelo para atualização de etapa"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    step_type: Optional[StepType] = None
    order: Optional[int] = Field(None, ge=1)
    description: Optional[str] = Field(None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    
class FlowStepResponse(FlowStepBase):
    """Modelo de resposta da etapa"""
    id: int
    flow_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class FlowBase(BaseModel):
    """Modelo base do flow"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do flow")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição do flow")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags para organização")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configurações específicas do flow")
    
class FlowCreate(FlowBase):
    """Modelo para criação de flow"""
    steps: List[FlowStepCreate] = Field(..., min_items=1, description="Etapas do flow")
    
class FlowUpdate(BaseModel):
    """Modelo para atualização de flow"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[FlowStatus] = None
    tags: Optional[List[str]] = None
    
class FlowResponse(FlowBase):
    """Modelo de resposta do flow"""
    id: int
    user_id: int
    status: FlowStatus
    created_at: datetime
    updated_at: Optional[datetime]
    last_executed: Optional[datetime]
    execution_count: int = 0
    estimated_time: Optional[int] = None  # em segundos
    steps: List[FlowStepResponse] = []
    step_count: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class FlowWithSteps(FlowResponse):
    """Modelo de resposta do flow com suas etapas"""
    steps: List[FlowStepResponse]
    
    class Config:
        from_attributes = True
        
class FlowExecutionRequest(BaseModel):
    """Modelo para solicitação de execução de flow"""
    flow_id: int
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados de entrada")
    auto_continue: bool = Field(default=True, description="Continuar automaticamente após pausas")
    
class FlowExecutionCreate(BaseModel):
    """Modelo para criação de execução de flow"""
    flow_id: int
    user_id: int
    trigger_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados de entrada")
    
class FlowExecutionStepResult(BaseModel):
    """Resultado de uma etapa da execução"""
    step_id: int
    step_name: str
    status: ExecutionStatus
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
class FlowExecutionResponse(BaseModel):
    """Modelo de resposta da execução de flow"""
    id: int
    flow_id: int
    flow_name: str
    user_id: int
    status: ExecutionStatus
    trigger_data: Optional[Dict[str, Any]] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    completed_steps: Optional[int] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    duration: Optional[float] = None
    time_saved: Optional[float] = None
    started_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steps_results: List[FlowExecutionStepResult] = []
    
    class Config:
        from_attributes = True

# Modelos SQLAlchemy (para banco de dados)
class Flow(Base):
    """Tabela de flows"""
    __tablename__ = "flows"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(FlowStatus), default=FlowStatus.DRAFT, nullable=False)
    tags = Column(Text, nullable=True)  # JSON array
    estimated_time = Column(Integer, nullable=True)  # em segundos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed = Column(DateTime(timezone=True), nullable=True)
    execution_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Flow(id={self.id}, name='{self.name}', status='{self.status}')>"

class FlowStep(Base):
    """Tabela de etapas dos flows"""
    __tablename__ = "flow_steps"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    flow_id = Column(UUIDColumn, ForeignKey('empl.flows.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    step_type = Column(SQLEnum(StepType), nullable=False)
    order = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    config = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FlowStep(id={self.id}, flow_id={self.flow_id}, name='{self.name}')>"

class FlowExecution(Base):
    """Tabela de execuções de flows"""
    __tablename__ = "flow_executions"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    flow_id = Column(UUIDColumn, ForeignKey('empl.flows.id'), nullable=False, index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    input_data = Column(Text, nullable=True)  # JSON string
    output_data = Column(Text, nullable=True)  # JSON string
    current_step = Column(Integer, nullable=True)
    total_steps = Column(Integer, nullable=False)
    completed_steps = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FlowExecution(id={self.id}, flow_id={self.flow_id}, status='{self.status}')>"

class FlowExecutionStep(Base):
    """Tabela de resultados das etapas de execução"""
    __tablename__ = "flow_execution_steps"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    execution_id = Column(UUIDColumn, ForeignKey('empl.flow_executions.id'), nullable=False, index=True)
    step_id = Column(UUIDColumn, ForeignKey('empl.flow_steps.id'), nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    input_data = Column(Text, nullable=True)  # JSON string
    output_data = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FlowExecutionStep(id={self.id}, execution_id={self.execution_id}, status='{self.status}')>"

class FlowTemplate(Base):
    """Tabela de templates de flows"""
    __tablename__ = "flow_templates"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    template_data = Column(Text, nullable=False)  # JSON string com estrutura do flow
    is_public = Column(Boolean, default=False, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FlowTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"

