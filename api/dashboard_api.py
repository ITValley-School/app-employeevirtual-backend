"""
API de dashboard - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from sqlalchemy.orm import Session

from schemas.dashboard.requests import DashboardMetricsRequest
from schemas.dashboard.responses import (
    DashboardOverviewResponse, 
    DashboardStatsResponse, 
    DashboardChartResponse,
    DashboardReportResponse
)
from services.dashboard_service import DashboardService
from mappers.dashboard_mapper import DashboardMapper
from factories.dashboard_factory import DashboardFactory
from config.database import db_config
from auth.dependencies import get_current_user
from data.entities.user_entities import UserEntity

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_dashboard_service(db: Session = Depends(db_config.get_session)) -> DashboardService:
    """Dependency para DashboardService"""
    return DashboardService(db)


@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca visão geral do dashboard
    
    Args:
        dashboard_service: Serviço de dashboard
        current_user: Usuário autenticado
        
    Returns:
        DashboardOverviewResponse: Visão geral do dashboard
    """
    # Service orquestra busca e validações
    overview = dashboard_service.get_overview(current_user.get_id())
    
    # Converte para Response
    return DashboardMapper.to_overview(overview)


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    period: str = Query("30d", description="Período (7d, 30d, 90d, 1y)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca estatísticas do dashboard
    
    Args:
        period: Período das estatísticas
        dashboard_service: Serviço de dashboard
        current_user: Usuário autenticado
        
    Returns:
        DashboardStatsResponse: Estatísticas do dashboard
    """
    # Service orquestra busca e validações
    stats = dashboard_service.get_stats(current_user.get_id(), period)
    
    # Converte para Response
    return DashboardMapper.to_stats(stats)


@router.get("/charts/usage", response_model=DashboardChartResponse)
async def get_usage_chart(
    period: str = Query("30d", description="Período (7d, 30d, 90d, 1y)"),
    chart_type: str = Query("line", description="Tipo do gráfico (line, bar, pie)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca gráfico de uso
    
    Args:
        period: Período do gráfico
        chart_type: Tipo do gráfico
        dashboard_service: Serviço de dashboard
        current_user: Usuário autenticado
        
    Returns:
        DashboardChartResponse: Dados do gráfico
    """
    # Service orquestra busca e validações
    chart_data = dashboard_service.get_usage_chart(current_user.get_id(), period, chart_type)
    
    # Converte para Response
    return DashboardMapper.to_chart(chart_data)


@router.get("/charts/performance", response_model=DashboardChartResponse)
async def get_performance_chart(
    period: str = Query("30d", description="Período (7d, 30d, 90d, 1y)"),
    chart_type: str = Query("line", description="Tipo do gráfico (line, bar, pie)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Busca gráfico de performance
    
    Args:
        period: Período do gráfico
        chart_type: Tipo do gráfico
        dashboard_service: Serviço de dashboard
        current_user: Usuário autenticado
        
    Returns:
        DashboardChartResponse: Dados do gráfico
    """
    # Service orquestra busca e validações
    chart_data = dashboard_service.get_performance_chart(current_user.get_id(), period, chart_type)
    
    # Converte para Response
    return DashboardMapper.to_chart(chart_data)


@router.get("/reports/execution", response_model=DashboardReportResponse)
async def get_execution_report(
    period: str = Query("30d", description="Período (7d, 30d, 90d, 1y)"),
    format: str = Query("json", description="Formato do relatório (json, csv, pdf)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Gera relatório de execuções
    
    Args:
        period: Período do relatório
        format: Formato do relatório
        dashboard_service: Serviço de dashboard
        current_user: Usuário autenticado
        
    Returns:
        DashboardReportResponse: Relatório gerado
    """
    # Service orquestra geração e validações
    report = dashboard_service.generate_execution_report(current_user.get_id(), period, format)
    
    # Converte para Response
    return DashboardMapper.to_report(report)


@router.get("/reports/usage", response_model=DashboardReportResponse)
async def get_usage_report(
    period: str = Query("30d", description="Período (7d, 30d, 90d, 1y)"),
    format: str = Query("json", description="Formato do relatório (json, csv, pdf)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Gera relatório de uso
    
    Args:
        period: Período do relatório
        format: Formato do relatório
        dashboard_service: Serviço de dashboard
        current_user: Usuário autenticado
        
    Returns:
        DashboardReportResponse: Relatório gerado
    """
    # Service orquestra geração e validações
    report = dashboard_service.generate_usage_report(current_user.get_id(), period, format)
    
    # Converte para Response
    return DashboardMapper.to_report(report)
