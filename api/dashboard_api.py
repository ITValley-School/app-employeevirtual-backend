"""
API de dashboard e métricas para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from models.dashboard_models import DashboardResponse, DashboardSummary
from models.user_models import UserResponse
from services.dashboard_service import DashboardService
from auth.dependencies import get_current_user
from data.database import get_db

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
async def get_user_dashboard(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna dashboard principal do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do dashboard
    """
    dashboard_service = DashboardService(db)
    
    dashboard_data = dashboard_service.get_user_dashboard(current_user.id)
    
    return dashboard_data

@router.get("/metrics")
async def get_user_metrics(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Métricas do usuário
    """
    dashboard_service = DashboardService(db)
    
    metrics = dashboard_service.get_user_metrics(current_user.id)
    
    return metrics

@router.get("/agents/stats")
async def get_agents_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas dos agentes do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Estatísticas dos agentes
    """
    dashboard_service = DashboardService(db)
    
    stats = dashboard_service.get_agents_stats(current_user.id)
    
    return stats

@router.get("/flows/stats")
async def get_flows_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas dos flows do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Estatísticas dos flows
    """
    dashboard_service = DashboardService(db)
    
    stats = dashboard_service.get_flows_stats(current_user.id)
    
    return stats

@router.get("/chat/stats")
async def get_chat_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas do chat do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Estatísticas do chat
    """
    dashboard_service = DashboardService(db)
    
    stats = dashboard_service.get_chat_stats(current_user.id)
    
    return stats

@router.get("/activity/timeline")
async def get_activity_timeline(
    days: int = 30,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna timeline de atividades do usuário
    
    Args:
        days: Número de dias para buscar
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Timeline de atividades
    """
    dashboard_service = DashboardService(db)
    
    timeline = dashboard_service.get_activity_timeline(current_user.id, days)
    
    return timeline

@router.get("/performance/overview")
async def get_performance_overview(
    period: str = "month",
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna visão geral de performance do usuário
    
    Args:
        period: Período (week, month, quarter, year)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Visão geral de performance
    """
    dashboard_service = DashboardService(db)
    
    overview = dashboard_service.get_performance_overview(current_user.id, period)
    
    return overview

@router.get("/usage/breakdown")
async def get_usage_breakdown(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna breakdown de uso por recurso
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Breakdown de uso
    """
    dashboard_service = DashboardService(db)
    
    breakdown = dashboard_service.get_usage_breakdown(current_user.id)
    
    return breakdown

@router.get("/system/overview")
async def get_system_overview(db: Session = Depends(get_db)):
    """
    Retorna visão geral do sistema (apenas para usuários enterprise)
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Visão geral do sistema
    """
    dashboard_service = DashboardService(db)
    
    overview = dashboard_service.get_system_overview()
    
    return overview

@router.get("/reports/generate")
async def generate_user_report(
    report_type: str,
    start_date: str,
    end_date: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera relatório personalizado para o usuário
    
    Args:
        report_type: Tipo de relatório
        start_date: Data de início (YYYY-MM-DD)
        end_date: Data de fim (YYYY-MM-DD)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Relatório gerado
    """
    dashboard_service = DashboardService(db)
    
    try:
        report = dashboard_service.generate_user_report(
            user_id=current_user.id,
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna insights gerados por IA baseados nos dados do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Insights de IA
    """
    dashboard_service = DashboardService(db)
    
    insights = dashboard_service.get_ai_insights(current_user.id)
    
    return insights

@router.post("/goals/set")
async def set_user_goals(
    goals: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Define metas para o usuário
    
    Args:
        goals: Metas a serem definidas
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Metas definidas
    """
    dashboard_service = DashboardService(db)
    
    try:
        user_goals = dashboard_service.set_user_goals(
            user_id=current_user.id,
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna progresso das metas do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Progresso das metas
    """
    dashboard_service = DashboardService(db)
    
    progress = dashboard_service.get_goals_progress(current_user.id)
    
    return progress

