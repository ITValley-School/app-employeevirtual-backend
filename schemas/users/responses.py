"""
Schemas de resposta para usuários
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
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

class UserResponse(BaseModel):
    """Response básico do usuário"""
    id: str = Field(..., description="UUID único do usuário")
    name: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="Email do usuário")
    plan: UserPlan = Field(..., description="Plano de assinatura")
    status: UserStatus = Field(..., description="Status do usuário")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de última atualização")
    last_login: Optional[datetime] = Field(None, description="Data do último login")

class UserDetailResponse(UserResponse):
    """Response detalhado do usuário"""
    total_agents: int = Field(default=0, description="Total de agentes criados")
    total_flows: int = Field(default=0, description="Total de flows criados")
    total_executions: int = Field(default=0, description="Total de execuções")

class UserListResponse(BaseModel):
    """Response para listagem de usuários"""
    users: list[UserResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de usuários")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")

class UserLoginResponse(BaseModel):
    """Response para login"""
    user: UserResponse = Field(..., description="Dados do usuário")
    access_token: str = Field(..., description="Token de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")

class UserStatsResponse(BaseModel):
    """Response para estatísticas do usuário"""
    user_id: str = Field(..., description="ID do usuário")
    total_agents: int = Field(..., description="Total de agentes")
    total_flows: int = Field(..., description="Total de flows")
    total_executions: int = Field(..., description="Total de execuções")
    last_activity: Optional[datetime] = Field(None, description="Última atividade")
