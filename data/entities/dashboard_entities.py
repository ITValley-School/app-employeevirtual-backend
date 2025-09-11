"""
Entidades de dados para dashboard e métricas
Responsabilidade: Mapeamento objeto-relacional e persistência
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Date, text
from sqlalchemy.sql import func
from data.base import Base


class UserMetricsEntity(Base):
    """Entidade de métricas por usuário"""
    __tablename__ = "user_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(String(36), primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(String(36), nullable=False, index=True)
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
        return f"<UserMetricsEntity(id={self.id}, user_id={self.user_id}, date={self.metric_date})>"


class AgentMetricsEntity(Base):
    """Entidade de métricas de agentes"""
    __tablename__ = "agent_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(String(36), primary_key=True, server_default=text("NEWID()"), index=True)
    agent_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    executions = Column(Integer, default=0, nullable=False)
    total_execution_time = Column(Float, default=0.0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    failed_executions = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AgentMetricsEntity(id={self.id}, agent_id={self.agent_id}, date={self.metric_date})>"


class FlowMetricsEntity(Base):
    """Entidade de métricas de flows"""
    __tablename__ = "flow_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(String(36), primary_key=True, server_default=text("NEWID()"), index=True)
    flow_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    executions = Column(Integer, default=0, nullable=False)
    total_execution_time = Column(Float, default=0.0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    failed_executions = Column(Integer, default=0, nullable=False)
    time_saved = Column(Float, default=0.0, nullable=False)  # em horas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FlowMetricsEntity(id={self.id}, flow_id={self.flow_id}, date={self.metric_date})>"


class SystemMetricsEntity(Base):
    """Entidade de métricas do sistema"""
    __tablename__ = "system_metrics"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(String(36), primary_key=True, server_default=text("NEWID()"), index=True)
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
        return f"<SystemMetricsEntity(id={self.id}, date={self.metric_date})>"
