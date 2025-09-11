"""
Entidades SQLAlchemy para flows/automações do sistema EmployeeVirtual
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Enum as SQLEnum, ForeignKey, text
from sqlalchemy.sql import func

from models.uuid_models import UUIDColumn
from data.base import Base
from models.flow_models import FlowStatus, ExecutionStatus, StepType


class FlowEntity(Base):
    """Entidade de flows"""
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
        return f"<FlowEntity(id={self.id}, name='{self.name}', status='{self.status}')>"


class FlowStepEntity(Base):
    """Entidade de etapas dos flows"""
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
        return f"<FlowStepEntity(id={self.id}, flow_id={self.flow_id}, name='{self.name}')>"


class FlowExecutionEntity(Base):
    """Entidade de execuções de flows"""
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
        return f"<FlowExecutionEntity(id={self.id}, flow_id={self.flow_id}, status='{self.status}')>"


class FlowExecutionStepEntity(Base):
    """Entidade de resultados das etapas de execução"""
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
        return f"<FlowExecutionStepEntity(id={self.id}, execution_id={self.execution_id}, status='{self.status}')>"


class FlowTemplateEntity(Base):
    """Entidade de templates de flows"""
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
        return f"<FlowTemplateEntity(id={self.id}, name='{self.name}', category='{self.category}')>"
