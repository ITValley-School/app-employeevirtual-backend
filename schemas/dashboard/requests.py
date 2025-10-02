"""
Schemas de requisição para dashboard
Seguindo padrão IT Valley Architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DashboardMetricsRequest(BaseModel):
    """Request para métricas do dashboard"""
    period: str = Field(default="30d", description="Período das métricas")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")

class DashboardStatsRequest(BaseModel):
    """Request para estatísticas do dashboard"""
    start_date: Optional[datetime] = Field(None, description="Data de início")
    end_date: Optional[datetime] = Field(None, description="Data de fim")
    granularity: str = Field(default="day", description="Granularidade dos dados")
