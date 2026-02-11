"""
Service de dashboard - Orquestrador de casos de uso
Seguindo padrão IT Valley Architecture
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from data.dashboard_repository import DashboardRepository
from factories.dashboard_factory import DashboardFactory


class DashboardService:
    """Service para orquestração de dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repository = DashboardRepository(db)
    
    def get_overview(self, user_id: str) -> Dict[str, Any]:
        """
        Busca visão geral do dashboard
        
        Args:
            user_id: ID do usuário
            
        Returns:
            dict: Visão geral do dashboard
        """
        # 1. Factory cria dados a partir do user_id
        overview_data = DashboardFactory.create_overview(user_id)
        
        # 2. Repository busca dados reais
        real_data = self.dashboard_repository.get_overview(user_id)
        
        # 3. Merge dos dados
        overview_data.update(real_data)
        
        return overview_data
    
    def get_stats(self, user_id: str, period: str) -> Dict[str, Any]:
        """
        Busca estatísticas do dashboard
        
        Args:
            user_id: ID do usuário
            period: Período das estatísticas
            
        Returns:
            dict: Estatísticas do dashboard
        """
        return self.dashboard_repository.get_stats(user_id, period)
    
    def get_usage_chart(self, user_id: str, period: str, chart_type: str) -> Dict[str, Any]:
        """
        Busca gráfico de uso
        
        Args:
            user_id: ID do usuário
            period: Período do gráfico
            chart_type: Tipo do gráfico
            
        Returns:
            dict: Dados do gráfico
        """
        return self.dashboard_repository.get_usage_chart(user_id, period, chart_type)
    
    def get_performance_chart(self, user_id: str, period: str, chart_type: str) -> Dict[str, Any]:
        """
        Busca gráfico de performance
        
        Args:
            user_id: ID do usuário
            period: Período do gráfico
            chart_type: Tipo do gráfico
            
        Returns:
            dict: Dados do gráfico
        """
        return self.dashboard_repository.get_performance_chart(user_id, period, chart_type)
    
    def generate_execution_report(self, user_id: str, period: str, format: str) -> Dict[str, Any]:
        """
        Gera relatório de execuções
        
        Args:
            user_id: ID do usuário
            period: Período do relatório
            format: Formato do relatório
            
        Returns:
            dict: Relatório gerado
        """
        return self.dashboard_repository.generate_execution_report(user_id, period, format)
    
    def generate_usage_report(self, user_id: str, period: str, format: str) -> Dict[str, Any]:
        """
        Gera relatório de uso
        
        Args:
            user_id: ID do usuário
            period: Período do relatório
            format: Formato do relatório
            
        Returns:
            dict: Relatório gerado
        """
        return self.dashboard_repository.generate_usage_report(user_id, period, format)
