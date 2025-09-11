"""
Modelos de domínio para usuários do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

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
    id: str = Field(..., description="UUID único do usuário")
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
    id: str = Field(..., description="UUID único do usuário")
    name: str
    email: str
    plan: UserPlan
    status: UserStatus
    created_at: datetime
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = {}
    
    class Config:
        from_attributes = True

