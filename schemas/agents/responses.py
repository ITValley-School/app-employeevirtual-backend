"""
Schemas de resposta para agentes
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    """Status do agente"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    ERROR = "error"

class AgentType(str, Enum):
    """Tipos de agente"""
    CHATBOT = "chatbot"
    ASSISTANT = "assistant"
    AUTOMATION = "automation"
    ANALYZER = "analyzer"

class AgentResponse(BaseModel):
    """Response básico do agente"""
    id: str = Field(..., description="UUID único do agente")
    name: str = Field(..., description="Nome do agente")
    description: Optional[str] = Field(None, description="Descrição do agente")
    type: AgentType = Field(..., description="Tipo do agente")
    status: AgentStatus = Field(..., description="Status do agente")
    model: str = Field(..., description="Modelo de IA")
    temperature: float = Field(..., description="Temperatura do modelo")
    max_tokens: int = Field(..., description="Máximo de tokens")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de última atualização")
    user_id: str = Field(..., description="ID do usuário proprietário")

class AgentDetailResponse(AgentResponse):
    """Response detalhado do agente"""
    instructions: str = Field(..., description="Instruções do agente")
    system_prompt: Optional[str] = Field(None, description="Prompt do sistema")
    total_executions: int = Field(default=0, description="Total de execuções")
    last_execution: Optional[datetime] = Field(None, description="Última execução")
    performance_score: Optional[float] = Field(None, description="Score de performance")

class AgentListResponse(BaseModel):
    """Response para listagem de agentes"""
    agents: List[AgentResponse] = Field(..., description="Lista de agentes")
    total: int = Field(..., description="Total de agentes")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")

class AgentExecuteResponse(BaseModel):
    """Response para execução de agente"""
    agent_id: str = Field(..., description="ID do agente")
    message: str = Field(..., description="Mensagem enviada")
    response: str = Field(..., description="Resposta do agente")
    execution_time: float = Field(..., description="Tempo de execução em segundos")
    tokens_used: int = Field(..., description="Tokens utilizados")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    timestamp: datetime = Field(..., description="Timestamp da execução")

class AgentStatsResponse(BaseModel):
    """Response para estatísticas do agente"""
    agent_id: str = Field(..., description="ID do agente")
    total_executions: int = Field(..., description="Total de execuções")
    avg_execution_time: float = Field(..., description="Tempo médio de execução")
    total_tokens_used: int = Field(..., description="Total de tokens utilizados")
    success_rate: float = Field(..., description="Taxa de sucesso")
    last_activity: Optional[datetime] = Field(None, description="Última atividade")
    performance_trend: str = Field(..., description="Tendência de performance")

class AgentTrainingResponse(BaseModel):
    """Response para treinamento de agente"""
    agent_id: str = Field(..., description="ID do agente")
    training_id: str = Field(..., description="ID do treinamento")
    status: str = Field(..., description="Status do treinamento")
    progress: float = Field(..., description="Progresso do treinamento")
    epochs_completed: int = Field(..., description="Épocas completadas")
    loss: Optional[float] = Field(None, description="Perda atual")
    accuracy: Optional[float] = Field(None, description="Precisão atual")
    started_at: datetime = Field(..., description="Início do treinamento")
    estimated_completion: Optional[datetime] = Field(None, description="Estimativa de conclusão")
