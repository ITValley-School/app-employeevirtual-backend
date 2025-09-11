"""
Modelos de domínio para dashboard e métricas do sistema EmployeeVirtual
Responsabilidade: Definir contratos e estruturas de dados de negócio (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class MetricType(str, Enum):
    """Tipos de métricas"""
    AGENT_EXECUTION = "agent_execution"
    FLOW_EXECUTION = "flow_execution"
    FILE_UPLOAD = "file_upload"
    CHAT_MESSAGE = "chat_message"
    USER_LOGIN = "user_login"
    TIME_SAVED = "time_saved"


class PeriodType(str, Enum):
    """Tipos de período para métricas"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class DashboardSummary(BaseModel):
    """Resumo do dashboard"""
    total_agents: int = 0
    total_flows: int = 0
    total_executions_today: int = 0
    total_executions_all_time: int = 0
    active_flows: int = 0
    paused_flows: int = 0
    error_flows: int = 0
    draft_flows: int = 0
    time_saved_today: float = 0.0  # em horas
    time_saved_all_time: float = 0.0  # em horas
    

class AgentMetrics(BaseModel):
    """Métricas de agentes"""
    agent_id: int
    agent_name: str
    total_executions: int = 0
    executions_today: int = 0
    executions_this_week: int = 0
    executions_this_month: int = 0
    average_execution_time: Optional[float] = None
    success_rate: float = 0.0
    last_used: Optional[datetime] = None
    

class FlowMetrics(BaseModel):
    """Métricas de flows"""
    flow_id: int
    flow_name: str
    total_executions: int = 0
    executions_today: int = 0
    executions_this_week: int = 0
    executions_this_month: int = 0
    average_execution_time: Optional[float] = None
    success_rate: float = 0.0
    last_executed: Optional[datetime] = None
    status: str
    

class UsageMetrics(BaseModel):
    """Métricas de uso"""
    date: date
    agent_executions: int = 0
    flow_executions: int = 0
    file_uploads: int = 0
    chat_messages: int = 0
    time_saved: float = 0.0  # em horas
    

class TimeSeriesData(BaseModel):
    """Dados de série temporal"""
    date: date
    value: float
    label: Optional[str] = None
    

class ChartData(BaseModel):
    """Dados para gráficos"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    

class DashboardResponse(BaseModel):
    """Resposta completa do dashboard"""
    summary: DashboardSummary
    top_agents: List[AgentMetrics]
    recent_flows: List[FlowMetrics]
    usage_chart: ChartData
    time_saved_chart: ChartData
    

class MetricFilter(BaseModel):
    """Filtros para métricas"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    agent_ids: Optional[List[int]] = None
    flow_ids: Optional[List[int]] = None
    metric_types: Optional[List[MetricType]] = None
    

class ReportRequest(BaseModel):
    """Solicitação de relatório"""
    report_type: str = Field(..., description="Tipo do relatório")
    period: PeriodType = Field(default=PeriodType.MONTHLY, description="Período do relatório")
    filters: Optional[MetricFilter] = None
    format: str = Field(default="json", description="Formato do relatório (json, csv, pdf)")

