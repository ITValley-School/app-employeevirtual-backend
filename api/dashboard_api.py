"""
API de dashboard e métricas para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from models.dashboard_models import DashboardResponse, DashboardSummary
from models.user_models import UserResponse
from services.dashboard_service import DashboardService
from itvalleysecurity.fastapi import require_access
from dependencies.service_providers import get_dashboard_service
router = APIRouter()
@router.get("/", response_model=DashboardResponse)
async def get_user_dashboard(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna dashboard principal do usuário
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Dados do dashboard
    """
    dashboard_data = dashboard_service.get_user_dashboard(user_token["sub"])
    return dashboard_data
@router.get("/metrics")
async def get_user_metrics(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna métricas do usuário
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Métricas do usuário
    """
    metrics = dashboard_service.get_user_metrics(user_token["sub"])
    return metrics
@router.get("/agents/stats")
async def get_agents_stats(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna estatísticas dos agentes do usuário
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Estatísticas dos agentes
    """
    stats = dashboard_service.get_agents_stats(user_token["sub"])
    return stats
@router.get("/flows/stats")
async def get_flows_stats(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna estatísticas dos flows do usuário
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Estatísticas dos flows
    """
    stats = dashboard_service.get_flows_stats(user_token["sub"])
    return stats
@router.get("/chat/stats")
async def get_chat_stats(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna estatísticas do chat do usuário
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Estatísticas do chat
    """
    stats = dashboard_service.get_chat_stats(user_token["sub"])
    return stats
@router.get("/activity/timeline")
async def get_activity_timeline(
    days: int = 30,
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna timeline de atividades do usuário
    Args:
        days: Número de dias para buscar
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Timeline de atividades
    """
    timeline = dashboard_service.get_activity_timeline(user_token["sub"], days)
    return timeline
@router.get("/performance/overview")
async def get_performance_overview(
    period: str = "month",
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna visão geral de performance do usuário
    Args:
        period: Período (week, month, quarter, year)
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Visão geral de performance
    """
    overview = dashboard_service.get_performance_overview(user_token["sub"], period)
    return overview
@router.get("/usage/breakdown")
async def get_usage_breakdown(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna breakdown de uso por recurso
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Breakdown de uso
    """
    breakdown = dashboard_service.get_usage_breakdown(user_token["sub"])
    return breakdown
@router.get("/system/overview")
async def get_system_overview(dashboard_service: DashboardService = Depends(get_dashboard_service)):
    """
    Retorna visão geral do sistema (apenas para usuários enterprise)
    Args:
        db: Sessão do banco de dados
    Returns:
        Visão geral do sistema
    """
    overview = dashboard_service.get_system_overview()
    return overview
@router.get("/reports/generate")
async def generate_user_report(
    report_type: str,
    start_date: str,
    end_date: str,
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Gera relatório personalizado para o usuário
    Args:
        report_type: Tipo de relatório
        start_date: Data de início (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Relatório gerado
    """
    try:
        report = dashboard_service.generate_user_report(
            user_id=user_token["sub"],
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )
@router.get("/insights/ai")
async def get_ai_insights(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna insights gerados por IA baseados nos dados do usuário
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Insights de IA
    """
    insights = dashboard_service.get_ai_insights(user_token["sub"])
    return insights
@router.post("/goals/set")
async def set_user_goals(
    goals: Dict[str, Any],
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Define metas para o usuário
    Args:
        goals: Metas a serem definidas
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Metas definidas
    """
    try:
        user_goals = dashboard_service.set_user_goals(
            user_id=user_token["sub"],
            goals=goals
        )
        return user_goals
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao definir metas: {str(e)}"
        )
@router.get("/goals/progress")
async def get_goals_progress(
    user_token = Depends(require_access),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna progresso das metas do usuário
    Args:
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
    Returns:
        Progresso das metas
    """
    progress = dashboard_service.get_goals_progress(user_token["sub"])
    return progress
