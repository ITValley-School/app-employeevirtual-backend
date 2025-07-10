"""
Modelos de dados para dashboard e métricas do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

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

# Modelos Pydantic (para API)
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

# Modelos SQLAlchemy (para banco de dados)
class UserMetrics(Base):
    """Tabela de métricas por usuário"""
    __tablename__ = "user_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    total_agents = Column(Integer, default=0, nullable=False)
    total_flows = Column(Integer, default=0, nullable=False)
    agent_executions = Column(Integer, default=0, nullable=False)
    flow_executions = Column(Integer, default=0, nullable=False)
    file_uploads = Column(Integer, default=0, nullable=False)
    chat_messages = Column(Integer, default=0, nullable=False)
    time_saved = Column(Float, default=0.0, nullable=False)  # em horas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserMetrics(id={self.id}, user_id={self.user_id}, date={self.metric_date})>"

class AgentMetricsDB(Base):
    """Tabela de métricas de agentes"""
    __tablename__ = "agent_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    executions = Column(Integer, default=0, nullable=False)
    total_execution_time = Column(Float, default=0.0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    failed_executions = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AgentMetricsDB(id={self.id}, agent_id={self.agent_id}, date={self.metric_date})>"

class FlowMetricsDB(Base):
    """Tabela de métricas de flows"""
    __tablename__ = "flow_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    executions = Column(Integer, default=0, nullable=False)
    total_execution_time = Column(Float, default=0.0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    failed_executions = Column(Integer, default=0, nullable=False)
    time_saved = Column(Float, default=0.0, nullable=False)  # em horas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FlowMetricsDB(id={self.id}, flow_id={self.flow_id}, date={self.metric_date})>"

class SystemMetrics(Base):
    """Tabela de métricas do sistema"""
    __tablename__ = "system_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    total_users = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    total_agents = Column(Integer, default=0, nullable=False)
    total_flows = Column(Integer, default=0, nullable=False)
    total_executions = Column(Integer, default=0, nullable=False)
    total_files = Column(Integer, default=0, nullable=False)
    total_storage_used = Column(Float, default=0.0, nullable=False)  # em GB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SystemMetrics(id={self.id}, date={self.metric_date})>"

