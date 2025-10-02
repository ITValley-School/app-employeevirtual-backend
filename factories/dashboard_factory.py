"""
Factory para dashboard
Cria objetos do domínio seguindo padrão IT Valley Architecture
"""
from typing import Dict, Any
from datetime import datetime

from schemas.dashboard.requests import DashboardMetricsRequest


class DashboardFactory:
    """Factory para criação de dashboard"""
    
    @staticmethod
    def create_overview(user_id: str) -> Dict[str, Any]:
        """
        Cria visão geral do dashboard
        
        Args:
            user_id: ID do usuário
            
        Returns:
            dict: Dados da visão geral
        """
        return {
            "user_id": user_id,
            "total_agents": 0,
            "total_flows": 0,
            "total_chats": 0,
            "total_executions": 0,
            "active_sessions": 0,
            "generated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_stats(user_id: str, period: str) -> Dict[str, Any]:
        """
        Cria estatísticas do dashboard
        
        Args:
            user_id: ID do usuário
            period: Período das estatísticas
            
        Returns:
            dict: Dados das estatísticas
        """
        return {
            "user_id": user_id,
            "period": period,
            "stats": {
                "executions": 0,
                "success_rate": 0.0,
                "avg_time": 0.0
            },
            "trends": {
                "executions": "stable",
                "performance": "stable"
            },
            "insights": [
                "Sistema funcionando normalmente",
                "Nenhuma anomalia detectada"
            ],
            "generated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_chart(user_id: str, period: str, chart_type: str) -> Dict[str, Any]:
        """
        Cria dados de gráfico
        
        Args:
            user_id: ID do usuário
            period: Período do gráfico
            chart_type: Tipo do gráfico
            
        Returns:
            dict: Dados do gráfico
        """
        return {
            "user_id": user_id,
            "type": chart_type,
            "period": period,
            "data": [],
            "labels": [],
            "generated_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_report(user_id: str, period: str, format: str, report_type: str) -> Dict[str, Any]:
        """
        Cria relatório
        
        Args:
            user_id: ID do usuário
            period: Período do relatório
            format: Formato do relatório
            report_type: Tipo do relatório
            
        Returns:
            dict: Dados do relatório
        """
        return {
            "user_id": user_id,
            "type": report_type,
            "period": period,
            "format": format,
            "data": [],
            "generated_at": datetime.utcnow()
        }
