"""
Schemas de requisição para usuários
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
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

class UserCreateRequest(BaseModel):
    """Request para criação de usuário"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=8, description="Senha do usuário")
    plan: UserPlan = Field(default=UserPlan.FREE, description="Plano de assinatura")

class UserUpdateRequest(BaseModel):
    """Request para atualização de usuário"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome completo do usuário")
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    plan: Optional[UserPlan] = Field(None, description="Plano de assinatura")
    status: Optional[UserStatus] = Field(None, description="Status do usuário")

class UserLoginRequest(BaseModel):
    """Request para login de usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

class UserPasswordChangeRequest(BaseModel):
    """Request para alteração de senha"""
    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(..., min_length=8, description="Nova senha")
