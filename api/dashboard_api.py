"""
API de dashboard e métricas para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional

from models.dashboard_models import DashboardResponse, UsageMetrics, MetricFilter
from models.user_models import UserResponse
from services.dashboard_service import DashboardService
from api.auth_api import get_current_user_dependency
from data.database import get_db

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
async def get_user_dashboard(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca dados completos do dashboard do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados completos do dashboard
    """
    dashboard_service = DashboardService(db)
    
    dashboard_data = dashboard_service.get_user_dashboard(current_user.id)
    
    return dashboard_data

@router.get("/summary")
async def get_dashboard_summary(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca resumo do dashboard
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resumo do dashboard
    """
    dashboard_service = DashboardService(db)
    
    summary = dashboard_service._get_dashboard_summary(current_user.id)
    
    return summary

@router.get("/agents/metrics")
async def get_agents_metrics(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca métricas dos agentes
    
    Args:
        limit: Limite de agentes
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Métricas dos agentes
    """
    dashboard_service = DashboardService(db)
    
    agents_metrics = dashboard_service._get_top_agents(current_user.id, limit)
    
    return {
        "agents": agents_metrics,
        "total": len(agents_metrics)
    }

@router.get("/flows/metrics")
async def get_flows_metrics(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca métricas dos flows
    
    Args:
        limit: Limite de flows
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Métricas dos flows
    """
    dashboard_service = DashboardService(db)
    
    flows_metrics = dashboard_service._get_recent_flows(current_user.id, limit)
    
    return {
        "flows": flows_metrics,
        "total": len(flows_metrics)
    }

@router.get("/usage", response_model=List[UsageMetrics])
async def get_usage_metrics(
    start_date: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    days: int = Query(30, ge=1, le=365, description="Número de dias (se start_date/end_date não fornecidos)"),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca métricas de uso por período
    
    Args:
        start_date: Data inicial
        end_date: Data final
        days: Número de dias (alternativa a start_date/end_date)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Métricas de uso
    """
    dashboard_service = DashboardService(db)
    
    # Definir período
    if not start_date or not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
    
    usage_metrics = dashboard_service.get_usage_metrics(
        current_user.id, start_date, end_date
    )
    
    return usage_metrics

@router.get("/charts/usage")
async def get_usage_chart(
    days: int = Query(30, ge=7, le=365),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca dados do gráfico de uso
    
    Args:
        days: Número de dias
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do gráfico de uso
    """
    dashboard_service = DashboardService(db)
    
    chart_data = dashboard_service._get_usage_chart(current_user.id, days)
    
    return chart_data

@router.get("/charts/time-saved")
async def get_time_saved_chart(
    days: int = Query(30, ge=7, le=365),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca dados do gráfico de tempo economizado
    
    Args:
        days: Número de dias
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do gráfico de tempo economizado
    """
    dashboard_service = DashboardService(db)
    
    chart_data = dashboard_service._get_time_saved_chart(current_user.id, days)
    
    return chart_data

@router.post("/metrics/update")
async def update_user_metrics(
    metric_date: Optional[date] = Query(None, description="Data das métricas (padrão: hoje)"),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Atualiza métricas do usuário
    
    Args:
        metric_date: Data das métricas
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
    """
    dashboard_service = DashboardService(db)
    
    success = dashboard_service.update_user_metrics(current_user.id, metric_date)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar métricas"
        )
    
    return {"message": "Métricas atualizadas com sucesso"}

@router.get("/reports/summary")
async def get_summary_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Gera relatório resumido
    
    Args:
        start_date: Data inicial
        end_date: Data final
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Relatório resumido
    """
    dashboard_service = DashboardService(db)
    
    # Definir período padrão (último mês)
    if not start_date or not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    
    # Buscar métricas do período
    usage_metrics = dashboard_service.get_usage_metrics(
        current_user.id, start_date, end_date
    )
    
    # Calcular totais
    total_agent_executions = sum(m.agent_executions for m in usage_metrics)
    total_flow_executions = sum(m.flow_executions for m in usage_metrics)
    total_file_uploads = sum(m.file_uploads for m in usage_metrics)
    total_chat_messages = sum(m.chat_messages for m in usage_metrics)
    total_time_saved = sum(m.time_saved for m in usage_metrics)
    
    # Buscar dados atuais
    summary = dashboard_service._get_dashboard_summary(current_user.id)
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": (end_date - start_date).days + 1
        },
        "totals": {
            "agent_executions": total_agent_executions,
            "flow_executions": total_flow_executions,
            "file_uploads": total_file_uploads,
            "chat_messages": total_chat_messages,
            "time_saved_hours": total_time_saved
        },
        "current_status": {
            "total_agents": summary.total_agents,
            "total_flows": summary.total_flows,
            "active_flows": summary.active_flows,
            "total_executions_all_time": summary.total_executions_all_time
        },
        "averages": {
            "daily_agent_executions": total_agent_executions / ((end_date - start_date).days + 1),
            "daily_flow_executions": total_flow_executions / ((end_date - start_date).days + 1),
            "daily_time_saved": total_time_saved / ((end_date - start_date).days + 1)
        }
    }

@router.get("/analytics/productivity")
async def get_productivity_analytics(
    days: int = Query(30, ge=7, le=365),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca análise de produtividade
    
    Args:
        days: Número de dias para análise
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Análise de produtividade
    """
    dashboard_service = DashboardService(db)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Buscar métricas
    usage_metrics = dashboard_service.get_usage_metrics(
        current_user.id, start_date, end_date
    )
    
    if not usage_metrics:
        return {
            "message": "Dados insuficientes para análise",
            "period": {"start_date": start_date, "end_date": end_date}
        }
    
    # Calcular tendências
    total_executions = [m.agent_executions + m.flow_executions for m in usage_metrics]
    time_saved = [m.time_saved for m in usage_metrics]
    
    # Análise simples de tendência
    if len(total_executions) >= 7:
        first_week_avg = sum(total_executions[:7]) / 7
        last_week_avg = sum(total_executions[-7:]) / 7
        execution_trend = "crescente" if last_week_avg > first_week_avg else "decrescente"
        
        first_week_time = sum(time_saved[:7]) / 7
        last_week_time = sum(time_saved[-7:]) / 7
        time_trend = "crescente" if last_week_time > first_week_time else "decrescente"
    else:
        execution_trend = "estável"
        time_trend = "estável"
    
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "trends": {
            "executions": execution_trend,
            "time_saved": time_trend
        },
        "totals": {
            "total_executions": sum(total_executions),
            "total_time_saved": sum(time_saved),
            "average_daily_executions": sum(total_executions) / len(total_executions),
            "average_daily_time_saved": sum(time_saved) / len(time_saved)
        },
        "insights": [
            f"Você executou {sum(total_executions)} automações nos últimos {days} dias",
            f"Economizou {sum(time_saved):.1f} horas no total",
            f"Tendência de execuções: {execution_trend}",
            f"Tendência de tempo economizado: {time_trend}"
        ]
    }

