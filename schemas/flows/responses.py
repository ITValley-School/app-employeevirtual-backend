"""
Schemas de resposta para flows
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class FlowStatus(str, Enum):
    """Status do flow"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RUNNING = "running"
    ERROR = "error"

class FlowType(str, Enum):
    """Tipos de flow"""
    AUTOMATION = "automation"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    NOTIFICATION = "notification"

class FlowResponse(BaseModel):
    """Response básico do flow"""
    id: str = Field(..., description="UUID único do flow")
    name: str = Field(..., description="Nome do flow")
    description: Optional[str] = Field(None, description="Descrição do flow")
    type: FlowType = Field(..., description="Tipo do flow")
    status: FlowStatus = Field(..., description="Status do flow")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de última atualização")
    user_id: str = Field(..., description="ID do usuário proprietário")

class FlowDetailResponse(FlowResponse):
    """Response detalhado do flow"""
    steps: List[Dict[str, Any]] = Field(..., description="Passos do flow")
    triggers: List[Dict[str, Any]] = Field(..., description="Triggers do flow")
    settings: Optional[Dict[str, Any]] = Field(None, description="Configurações do flow")
    total_executions: int = Field(default=0, description="Total de execuções")
    last_execution: Optional[datetime] = Field(None, description="Última execução")
    success_rate: Optional[float] = Field(None, description="Taxa de sucesso")

class FlowListResponse(BaseModel):
    """Response para listagem de flows"""
    flows: List[FlowResponse] = Field(..., description="Lista de flows")
    total: int = Field(..., description="Total de flows")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")

class FlowExecuteResponse(BaseModel):
    """Response para execução de flow"""
    flow_id: str = Field(..., description="ID do flow")
    input_data: Dict[str, Any] = Field(..., description="Dados de entrada")
    output_data: Dict[str, Any] = Field(..., description="Dados de saída")
    execution_time: float = Field(..., description="Tempo de execução em segundos")
    steps_completed: int = Field(..., description="Passos completados")
    session_id: Optional[str] = Field(None, description="ID da sessão")

class FlowStatsResponse(BaseModel):
    """Response para estatísticas do flow"""
    flow_id: str = Field(..., description="ID do flow")
    total_executions: int = Field(..., description="Total de execuções")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    avg_execution_time: float = Field(..., description="Tempo médio de execução")
    success_rate: float = Field(..., description="Taxa de sucesso")
    last_activity: Optional[datetime] = Field(None, description="Última atividade")
    performance_trend: str = Field(..., description="Tendência de performance")
