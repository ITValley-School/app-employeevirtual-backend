"""
Schemas de requisição para flows
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
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

class FlowCreateRequest(BaseModel):
    """Request para criação de flow"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do flow")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do flow")
    type: FlowType = Field(..., description="Tipo do flow")
    steps: List[Dict[str, Any]] = Field(..., description="Passos do flow")
    triggers: List[Dict[str, Any]] = Field(..., description="Triggers do flow")
    settings: Optional[Dict[str, Any]] = Field(None, description="Configurações do flow")

class FlowUpdateRequest(BaseModel):
    """Request para atualização de flow"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    steps: Optional[List[Dict[str, Any]]] = None
    triggers: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[FlowStatus] = None

class FlowExecuteRequest(BaseModel):
    """Request para execução de flow"""
    trigger_data: Dict[str, Any] = Field(..., description="Dados do trigger")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    user_id: Optional[str] = Field(None, description="ID do usuário")
