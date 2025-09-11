"""
Modelos de domínio para flows/automações do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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

