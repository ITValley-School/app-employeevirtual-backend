"""
Mapper para dashboard
Converte entre Entity (domínio) e Response (API)
Seguindo padrão IT Valley Architecture
"""
from typing import Dict, Any
from datetime import datetime

from schemas.dashboard.responses import (
    DashboardOverviewResponse, 
    DashboardStatsResponse, 
    DashboardChartResponse,
    DashboardReportResponse
)


class DashboardMapper:
    """Mapper para conversão de dashboard"""
    
    @staticmethod
    def to_overview(data: Dict[str, Any]) -> DashboardOverviewResponse:
        """
        Converte dados para DashboardOverviewResponse
        
        Args:
            data: Dados do dashboard
            
        Returns:
            DashboardOverviewResponse: Visão geral formatada
        """
        return DashboardOverviewResponse(
            user_id=data.get("user_id", ""),
            total_agents=data.get("total_agents", 0),
            total_flows=data.get("total_flows", 0),
            total_chats=data.get("total_chats", 0),
            total_executions=data.get("total_executions", 0),
            active_sessions=data.get("active_sessions", 0),
            generated_at=datetime.utcnow()
        )
    
    @staticmethod
    def to_stats(data: Dict[str, Any]) -> DashboardStatsResponse:
        """
        Converte dados para DashboardStatsResponse
        
        Args:
            data: Dados de estatísticas
            
        Returns:
            DashboardStatsResponse: Estatísticas formatadas
        """
        return DashboardStatsResponse(
            user_id=data.get("user_id", ""),
            stats=data.get("stats", {}),
            trends=data.get("trends", {}),
            insights=data.get("insights", []),
            generated_at=datetime.utcnow()
        )
    
    @staticmethod
    def to_chart(data: Dict[str, Any]) -> DashboardChartResponse:
        """
        Converte dados para DashboardChartResponse
        
        Args:
            data: Dados do gráfico
            
        Returns:
            DashboardChartResponse: Gráfico formatado
        """
        return DashboardChartResponse(
            chart_type=data.get("type", "line"),
            period=data.get("period", "30d"),
            data=data.get("data", []),
            labels=data.get("labels", []),
            generated_at=datetime.utcnow()
        )
    
    @staticmethod
    def to_report(data: Dict[str, Any]) -> DashboardReportResponse:
        """
        Converte dados para DashboardReportResponse
        
        Args:
            data: Dados do relatório
            
        Returns:
            DashboardReportResponse: Relatório formatado
        """
        return DashboardReportResponse(
            report_type=data.get("type", "execution"),
            period=data.get("period", "30d"),
            format=data.get("format", "json"),
            data=data.get("data", []),
            generated_at=datetime.utcnow()
        )
