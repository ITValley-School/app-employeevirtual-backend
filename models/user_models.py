"""
Modelos de dados para usuários do sistema EmployeeVirtual
"""
import os
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# Configuração de schema baseada no tipo de banco
USE_SCHEMA = not os.getenv("DATABASE_URL", "").startswith("sqlite")
SCHEMA_CONFIG = {'schema': 'empl'} if USE_SCHEMA else {}

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

# Modelos Pydantic (para API)
class UserBase(BaseModel):
    """Modelo base do usuário"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    plan: UserPlan = Field(default=UserPlan.FREE, description="Plano de assinatura")
    
class UserCreate(UserBase):
    """Modelo para criação de usuário"""
    password: str = Field(..., min_length=8, description="Senha do usuário")
    
class UserUpdate(BaseModel):
    """Modelo para atualização de usuário"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    plan: Optional[UserPlan] = None
    status: Optional[UserStatus] = None
    
class UserResponse(UserBase):
    """Modelo de resposta do usuário"""
    id: int
    status: Optional[UserStatus] = UserStatus.ACTIVE
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    total_agents: Optional[int] = 0
    total_flows: Optional[int] = 0
    total_executions: Optional[int] = 0
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Modelo para login"""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """Modelo para perfil do usuário"""
    id: int
    name: str
    email: str
    plan: UserPlan
    status: UserStatus
    created_at: datetime
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = {}
    
    class Config:
        from_attributes = True

# Modelos SQLAlchemy (para banco de dados)
class User(Base):
    """Tabela de usuários"""
    __tablename__ = "users"
    __table_args__ = SCHEMA_CONFIG
    
    id = Column(Integer, primary_key=True, index=True)
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
        return f"<User(id={self.id}, email='{self.email}', plan='{self.plan}')>"

class UserSession(Base):
    """Tabela de sessões de usuário"""
    __tablename__ = "user_sessions"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"

class UserActivity(Base):
    """Tabela de atividades do usuário"""
    __tablename__ = "user_activities"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # login, agent_created, flow_executed, etc.
    description = Column(Text, nullable=True)
    activity_metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"

