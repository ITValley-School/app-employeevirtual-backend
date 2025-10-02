"""
Entidades SQLAlchemy para usuários do sistema EmployeeVirtual
"""
import os
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum, text
from sqlalchemy.sql import func

from data.base import Base
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum as SQLEnum, text
from sqlalchemy.sql import func
from enum import Enum

# Enums locais
class UserPlan(str, Enum):
    """Planos de assinatura disponíveis"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserStatus(str, Enum):
    """Status do usuário"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

# UUID Column removido - usando Column(String(32)) diretamente


# Configuração de schema baseada no tipo de banco
USE_SCHEMA = True  # Usar schema para Azure SQL
SCHEMA_CONFIG = {'schema': 'empl'} if USE_SCHEMA else {}


class UserEntity(Base):
    """Entidade de usuários"""
    __tablename__ = "users"
    __table_args__ = SCHEMA_CONFIG
    
    id = Column(String(32), primary_key=True, server_default=text("NEWID()"), index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    plan = Column(SQLEnum(UserPlan), default=UserPlan.FREE, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    preferences = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserEntity(id={self.id}, email='{self.email}', plan='{self.plan}')>"


class UserSessionEntity(Base):
    """Entidade de sessões de usuário"""
    __tablename__ = "user_sessions"
    __table_args__ = SCHEMA_CONFIG
    
    id = Column(String(32), primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(String(32), nullable=False, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<UserSessionEntity(id={self.id}, user_id={self.user_id})>"


class UserActivityEntity(Base):
    """Entidade de atividades do usuário"""
    __tablename__ = "user_activities"
    __table_args__ = SCHEMA_CONFIG
    
    id = Column(String(32), primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(String(32), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # login, agent_created, flow_executed, etc.
    description = Column(Text, nullable=True)
    activity_metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserActivityEntity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"
