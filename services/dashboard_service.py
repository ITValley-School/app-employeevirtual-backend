"""
Serviço de dashboard para o sistema EmployeeVirtual - Nova implementação
Usa apenas repositories para acesso a dados
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from data.dashboard_repository import DashboardRepository
from data.agent_repository import AgentRepository
from data.user_repository import UserRepository
from models.dashboard_models import (
    DashboardSummary, AgentMetrics, FlowMetrics, UsageMetrics,
    MetricType, PeriodType
)


class DashboardService:
    """Serviço para gerenciamento de dashboard e métricas - Nova implementação"""
    
    def __init__(self, db: Session):
        self.dashboard_repository = DashboardRepository(db)
        self.agent_repository = AgentRepository(db)
        self.user_repository = UserRepository(db)
    
    def get_dashboard_summary(self, user_id: int) -> DashboardSummary:
        """
        Busca resumo geral do dashboard
        
        Args:
            user_id: ID do usuário
            
        Returns:
            DashboardSummary: Resumo do dashboard
        """
        summary_data = self.dashboard_repository.get_dashboard_summary(user_id)
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="dashboard_accessed",
            description="Dashboard acessado"
        )
        
        return DashboardSummary(
            total_agents=summary_data['total_agents'],
            total_flows=summary_data['total_flows'],
            total_executions_today=summary_data['total_executions_today'],
            total_executions_all_time=summary_data['total_executions_all_time'],
            active_flows=summary_data['active_flows'],
            paused_flows=summary_data['paused_flows'],
            error_flows=summary_data['error_flows'],
            draft_flows=summary_data['draft_flows'],
            time_saved_today=summary_data['time_saved_today'],
            time_saved_all_time=summary_data['time_saved_all_time']
        )
    
    def get_agent_metrics(self, user_id: int, agent_id: int = None, days: int = 30) -> List[AgentMetrics]:
        """
        Busca métricas de agentes
        
        Args:
            user_id: ID do usuário
            agent_id: ID específico do agente (opcional)
            days: Período em dias
            
        Returns:
            Lista de métricas de agentes
        """
        metrics_data = self.dashboard_repository.get_agent_metrics(user_id, agent_id, days)
        
        return [
            AgentMetrics(
                agent_id=metric['agent_id'],
                agent_name=metric['agent_name'],
                total_executions=metric['total_executions'],
                executions_today=metric['executions_today'],
                executions_this_week=metric['executions_this_week'],
                avg_duration=metric['avg_duration'],
                total_time_saved=metric['total_time_saved'],
                successful_executions=metric['successful_executions'],
                failed_executions=metric['failed_executions'],
                success_rate=metric['success_rate']
            )
            for metric in metrics_data
        ]
    
    def get_flow_metrics(self, user_id: int, flow_id: int = None, days: int = 30) -> List[FlowMetrics]:
        """
        Busca métricas de flows
        
        Args:
            user_id: ID do usuário
            flow_id: ID específico do flow (opcional)
            days: Período em dias
            
        Returns:
            Lista de métricas de flows
        """
        metrics_data = self.dashboard_repository.get_flow_metrics(user_id, flow_id, days)
        
        return [
            FlowMetrics(
                flow_id=metric['flow_id'],
                flow_name=metric['flow_name'],
                status=metric['status'],
                total_executions=metric['total_executions'],
                avg_duration=metric['avg_duration'],
                total_time_saved=metric['total_time_saved'],
                successful_executions=metric['successful_executions'],
                failed_executions=metric['failed_executions'],
                success_rate=metric['success_rate']
            )
            for metric in metrics_data
        ]
    
    def get_user_metrics(self, user_id: int) -> UsageMetrics:
        """
        Busca métricas consolidadas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            UserMetrics: Métricas do usuário
        """
        metrics_data = self.dashboard_repository.get_user_metrics(user_id)
        
        if not metrics_data:
            raise ValueError("Usuário não encontrado")
        
        return UsageMetrics(
            user_id=metrics_data['user_id'],
            name=metrics_data['name'],
            email=metrics_data['email'],
            plan=metrics_data['plan'],
            created_at=metrics_data['created_at'],
            last_login=metrics_data['last_login'],
            activity_summary=metrics_data['activity_summary'],
            dashboard_summary=DashboardSummary(**metrics_data['dashboard_summary']),
            file_metrics=metrics_data['file_metrics'],
            chat_metrics=metrics_data['chat_metrics']
        )
    
    def get_daily_metrics(self, user_id: int, metric_type: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """
        Busca métricas diárias
        
        Args:
            user_id: ID do usuário
            metric_type: Tipo de métrica específica
            days: Período em dias
            
        Returns:
            Lista de métricas diárias
        """
        return self.dashboard_repository.get_daily_metrics(user_id, metric_type, days)
    
    def get_weekly_metrics(self, user_id: int, weeks: int = 12) -> List[Dict[str, Any]]:
        """
        Busca métricas semanais
        
        Args:
            user_id: ID do usuário
            weeks: Período em semanas
            
        Returns:
            Lista de métricas semanais
        """
        return self.dashboard_repository.get_weekly_metrics(user_id, weeks)
    
    def get_file_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Busca métricas de arquivos
        
        Args:
            user_id: ID do usuário
            days: Período em dias
            
        Returns:
            Métricas de arquivos
        """
        return self.dashboard_repository.get_file_metrics(user_id, days)
    
    def get_chat_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Busca métricas de chat
        
        Args:
            user_id: ID do usuário
            days: Período em dias
            
        Returns:
            Métricas de chat
        """
        return self.dashboard_repository.get_chat_metrics(user_id, days)
    
    def get_performance_report(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Gera relatório de performance
        
        Args:
            user_id: ID do usuário
            days: Período em dias
            
        Returns:
            Relatório de performance
        """
        report = self.dashboard_repository.get_performance_report(user_id, days)
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="report_generated",
            description=f"Relatório de performance gerado para {days} dias"
        )
        
        return report
    
    def get_agent_performance(self, user_id: int, agent_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Busca performance detalhada de um agente
        
        Args:
            user_id: ID do usuário
            agent_id: ID do agente
            days: Período em dias
            
        Returns:
            Performance do agente
        """
        # Verificar se agente pertence ao usuário
        agent = self.agent_repository.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Buscar métricas do agente
        agent_metrics = self.dashboard_repository.get_agent_metrics(user_id, agent_id, days)
        if not agent_metrics:
            return {
                'agent_id': agent_id,
                'agent_name': agent.name,
                'no_data': True
            }
        
        metric = agent_metrics[0]
        
        # Buscar execuções recentes
        recent_executions = self.agent_repository.get_agent_executions(
            agent_id, limit=10, status=None
        )
        
        return {
            'agent_id': agent_id,
            'agent_name': agent.name,
            'description': agent.description,
            'total_executions': metric['total_executions'],
            'executions_today': metric['executions_today'],
            'executions_this_week': metric['executions_this_week'],
            'avg_duration': metric['avg_duration'],
            'total_time_saved': metric['total_time_saved'],
            'success_rate': metric['success_rate'],
            'recent_executions': [
                {
                    'id': exec.id,
                    'status': exec.status,
                    'duration': exec.duration,
                    'time_saved': exec.time_saved,
                    'created_at': exec.created_at
                }
                for exec in recent_executions
            ]
        }
    
    def get_productivity_insights(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Gera insights de produtividade
        
        Args:
            user_id: ID do usuário
            days: Período em dias
            
        Returns:
            Insights de produtividade
        """
        # Buscar dados base
        dashboard_summary = self.dashboard_repository.get_dashboard_summary(user_id)
        agent_metrics = self.dashboard_repository.get_agent_metrics(user_id, days=days)
        daily_metrics = self.dashboard_repository.get_daily_metrics(user_id, days=days)
        
        # Calcular insights
        total_time_saved = dashboard_summary['time_saved_all_time']
        avg_daily_executions = sum(metric['total_executions'] for metric in agent_metrics) / max(days, 1)
        
        # Agente mais produtivo
        most_productive_agent = None
        if agent_metrics:
            most_productive_agent = max(agent_metrics, key=lambda x: x['total_time_saved'])
        
        # Tendência (comparando primeira vs segunda metade do período)
        mid_point = days // 2
        first_half_executions = sum(
            metric['count'] for metric in daily_metrics[-mid_point:]
        ) if len(daily_metrics) >= mid_point else 0
        
        second_half_executions = sum(
            metric['count'] for metric in daily_metrics[:mid_point]
        ) if len(daily_metrics) >= mid_point else 0
        
        trend = "crescente" if first_half_executions > second_half_executions else "decrescente"
        
        return {
            'period_days': days,
            'total_time_saved_hours': total_time_saved,
            'total_time_saved_days': round(total_time_saved / 24, 2),
            'avg_daily_executions': round(avg_daily_executions, 1),
            'most_productive_agent': {
                'name': most_productive_agent['agent_name'],
                'time_saved': most_productive_agent['total_time_saved']
            } if most_productive_agent else None,
            'trend': trend,
            'recommendations': self._generate_recommendations(dashboard_summary, agent_metrics)
        }
    
    def _generate_recommendations(self, dashboard_summary: Dict[str, Any], 
                                agent_metrics: List[Dict[str, Any]]) -> List[str]:
        """
        Gera recomendações baseadas nas métricas
        
        Args:
            dashboard_summary: Resumo do dashboard
            agent_metrics: Métricas dos agentes
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        # Recomendações baseadas em agentes com baixa performance
        low_performance_agents = [
            agent for agent in agent_metrics 
            if agent['success_rate'] < 80 and agent['total_executions'] > 5
        ]
        
        if low_performance_agents:
            recommendations.append(
                f"Revisar configuração de {len(low_performance_agents)} agente(s) com taxa de sucesso abaixo de 80%"
            )
        
        # Recomendações baseadas em flows com erro
        if dashboard_summary['error_flows'] > 0:
            recommendations.append(
                f"Corrigir {dashboard_summary['error_flows']} flow(s) com erro"
            )
        
        # Recomendações baseadas em flows pausados
        if dashboard_summary['paused_flows'] > 0:
            recommendations.append(
                f"Revisar {dashboard_summary['paused_flows']} flow(s) pausado(s)"
            )
        
        # Recomendação para aumentar automação
        if dashboard_summary['total_agents'] < 3:
            recommendations.append(
                "Considere criar mais agentes para automatizar outras tarefas"
            )
        
        # Recomendação baseada em tempo economizado
        if dashboard_summary['time_saved_today'] < 1:
            recommendations.append(
                "Execute mais automações para economizar mais tempo hoje"
            )
        
        return recommendations if recommendations else ["Ótimo trabalho! Continue usando as automações."]
