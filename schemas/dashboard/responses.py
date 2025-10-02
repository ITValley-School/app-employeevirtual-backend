"""
Schemas de resposta para dashboard
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DashboardMetricsResponse(BaseModel):
    """Response para métricas do dashboard"""
    user_id: str = Field(..., description="ID do usuário")
    total_agents: int = Field(..., description="Total de agentes")
    total_flows: int = Field(..., description="Total de flows")
    total_chats: int = Field(..., description="Total de chats")
    total_executions: int = Field(..., description="Total de execuções")
    period: str = Field(..., description="Período das métricas")
    generated_at: datetime = Field(..., description="Data de geração")

class DashboardStatsResponse(BaseModel):
    """Response para estatísticas do dashboard"""
    user_id: str = Field(..., description="ID do usuário")
    stats: Dict[str, Any] = Field(..., description="Estatísticas detalhadas")
    trends: Dict[str, str] = Field(..., description="Tendências")
    insights: List[str] = Field(..., description="Insights gerados")
    generated_at: datetime = Field(..., description="Data de geração")
