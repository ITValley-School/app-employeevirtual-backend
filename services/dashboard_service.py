"""
Serviço de dashboard e métricas para o sistema EmployeeVirtual
"""
import json
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from models.dashboard_models import (
    UserMetrics, AgentMetricsDB, FlowMetricsDB, SystemMetrics,
    DashboardSummary, AgentMetrics as AgentMetricsModel, FlowMetrics as FlowMetricsModel,
    UsageMetrics, TimeSeriesData, ChartData, DashboardResponse, MetricFilter
)
from models.agent_models import Agent, AgentExecutionDB
from models.flow_models import Flow, FlowExecution, FlowStatus
from models.chat_models import Message
from models.file_models import File


class DashboardService:
    """Serviço para dashboard e métricas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_dashboard(self, user_id: int) -> DashboardResponse:
        """
        Busca dados completos do dashboard do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            DashboardResponse: Dados completos do dashboard
        """
        # Resumo geral
        summary = self._get_dashboard_summary(user_id)
        
        # Top agentes
        top_agents = self._get_top_agents(user_id, limit=5)
        
        # Flows recentes
        recent_flows = self._get_recent_flows(user_id, limit=5)
        
        # Gráfico de uso
        usage_chart = self._get_usage_chart(user_id, days=30)
        
        # Gráfico de tempo economizado
        time_saved_chart = self._get_time_saved_chart(user_id, days=30)
        
        return DashboardResponse(
            summary=summary,
            top_agents=top_agents,
            recent_flows=recent_flows,
            usage_chart=usage_chart,
            time_saved_chart=time_saved_chart
        )
    
    def _get_dashboard_summary(self, user_id: int) -> DashboardSummary:
        """Busca resumo do dashboard"""
        today = date.today()
        
        # Contar agentes
        total_agents = self.db.query(Agent).filter(Agent.user_id == user_id).count()
        
        # Contar flows por status
        flow_counts = self.db.query(
            Flow.status,
            func.count(Flow.id)
        ).filter(Flow.user_id == user_id).group_by(Flow.status).all()
        
        total_flows = sum(count for _, count in flow_counts)
        active_flows = next((count for status, count in flow_counts if status == FlowStatus.ACTIVE), 0)
        paused_flows = next((count for status, count in flow_counts if status == FlowStatus.PAUSED), 0)
        error_flows = next((count for status, count in flow_counts if status == FlowStatus.ERROR), 0)
        draft_flows = next((count for status, count in flow_counts if status == FlowStatus.DRAFT), 0)
        
        # Execuções hoje
        executions_today = (
            self.db.query(AgentExecutionDB).filter(
                and_(
                    AgentExecutionDB.user_id == user_id,
                    func.date(AgentExecutionDB.created_at) == today
                )
            ).count() +
            self.db.query(FlowExecution).filter(
                and_(
                    FlowExecution.user_id == user_id,
                    func.date(FlowExecution.started_at) == today
                )
            ).count()
        )
        
        # Execuções totais
        executions_all_time = (
            self.db.query(AgentExecutionDB).filter(AgentExecutionDB.user_id == user_id).count() +
            self.db.query(FlowExecution).filter(FlowExecution.user_id == user_id).count()
        )
        
        # Tempo economizado
        today_metrics = self.db.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date == today
            )
        ).first()
        
        time_saved_today = today_metrics.time_saved if today_metrics else 0.0
        
        # Tempo economizado total
        total_time_saved = self.db.query(
            func.sum(UserMetrics.time_saved)
        ).filter(UserMetrics.user_id == user_id).scalar() or 0.0
        
        return DashboardSummary(
            total_agents=total_agents,
            total_flows=total_flows,
            total_executions_today=executions_today,
            total_executions_all_time=executions_all_time,
            active_flows=active_flows,
            paused_flows=paused_flows,
            error_flows=error_flows,
            draft_flows=draft_flows,
            time_saved_today=time_saved_today,
            time_saved_all_time=total_time_saved
        )
    
    def _get_top_agents(self, user_id: int, limit: int = 5) -> List[AgentMetricsModel]:
        """Busca top agentes por uso"""
        agents = self.db.query(Agent).filter(
            Agent.user_id == user_id
        ).order_by(desc(Agent.usage_count)).limit(limit).all()
        
        result = []
        today = date.today()
        week_start = today - timedelta(days=7)
        month_start = today - timedelta(days=30)
        
        for agent in agents:
            # Execuções hoje
            executions_today = self.db.query(AgentExecutionDB).filter(
                and_(
                    AgentExecutionDB.agent_id == agent.id,
                    func.date(AgentExecutionDB.created_at) == today
                )
            ).count()
            
            # Execuções esta semana
            executions_this_week = self.db.query(AgentExecutionDB).filter(
                and_(
                    AgentExecutionDB.agent_id == agent.id,
                    func.date(AgentExecutionDB.created_at) >= week_start
                )
            ).count()
            
            # Execuções este mês
            executions_this_month = self.db.query(AgentExecutionDB).filter(
                and_(
                    AgentExecutionDB.agent_id == agent.id,
                    func.date(AgentExecutionDB.created_at) >= month_start
                )
            ).count()
            
            # Tempo médio de execução
            avg_time = self.db.query(
                func.avg(AgentExecutionDB.execution_time)
            ).filter(AgentExecutionDB.agent_id == agent.id).scalar()
            
            # Taxa de sucesso
            total_executions = self.db.query(AgentExecutionDB).filter(
                AgentExecutionDB.agent_id == agent.id
            ).count()
            
            successful_executions = self.db.query(AgentExecutionDB).filter(
                and_(
                    AgentExecutionDB.agent_id == agent.id,
                    AgentExecutionDB.success == True
                )
            ).count()
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0.0
            
            result.append(AgentMetricsModel(
                agent_id=agent.id,
                agent_name=agent.name,
                total_executions=total_executions,
                executions_today=executions_today,
                executions_this_week=executions_this_week,
                executions_this_month=executions_this_month,
                average_execution_time=avg_time,
                success_rate=success_rate,
                last_used=agent.last_used
            ))
        
        return result
    
    def _get_recent_flows(self, user_id: int, limit: int = 5) -> List[FlowMetricsModel]:
        """Busca flows recentes"""
        flows = self.db.query(Flow).filter(
            Flow.user_id == user_id
        ).order_by(desc(Flow.last_executed)).limit(limit).all()
        
        result = []
        today = date.today()
        week_start = today - timedelta(days=7)
        month_start = today - timedelta(days=30)
        
        for flow in flows:
            # Execuções hoje
            executions_today = self.db.query(FlowExecution).filter(
                and_(
                    FlowExecution.flow_id == flow.id,
                    func.date(FlowExecution.started_at) == today
                )
            ).count()
            
            # Execuções esta semana
            executions_this_week = self.db.query(FlowExecution).filter(
                and_(
                    FlowExecution.flow_id == flow.id,
                    func.date(FlowExecution.started_at) >= week_start
                )
            ).count()
            
            # Execuções este mês
            executions_this_month = self.db.query(FlowExecution).filter(
                and_(
                    FlowExecution.flow_id == flow.id,
                    func.date(FlowExecution.started_at) >= month_start
                )
            ).count()
            
            # Tempo médio de execução
            avg_time = self.db.query(
                func.avg(FlowExecution.execution_time)
            ).filter(FlowExecution.flow_id == flow.id).scalar()
            
            # Taxa de sucesso
            total_executions = flow.execution_count
            
            successful_executions = self.db.query(FlowExecution).filter(
                and_(
                    FlowExecution.flow_id == flow.id,
                    FlowExecution.status == "completed"
                )
            ).count()
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0.0
            
            result.append(FlowMetricsModel(
                flow_id=flow.id,
                flow_name=flow.name,
                total_executions=total_executions,
                executions_today=executions_today,
                executions_this_week=executions_this_week,
                executions_this_month=executions_this_month,
                average_execution_time=avg_time,
                success_rate=success_rate,
                last_executed=flow.last_executed,
                status=flow.status
            ))
        
        return result
    
    def _get_usage_chart(self, user_id: int, days: int = 30) -> ChartData:
        """Gera dados do gráfico de uso"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Buscar métricas diárias
        metrics = self.db.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date >= start_date,
                UserMetrics.metric_date <= end_date
            )
        ).order_by(UserMetrics.metric_date).all()
        
        # Criar dados para o gráfico
        labels = []
        agent_data = []
        flow_data = []
        chat_data = []
        
        # Preencher todos os dias
        current_date = start_date
        metrics_dict = {m.metric_date: m for m in metrics}
        
        while current_date <= end_date:
            labels.append(current_date.strftime("%d/%m"))
            
            metric = metrics_dict.get(current_date)
            if metric:
                agent_data.append(metric.agent_executions)
                flow_data.append(metric.flow_executions)
                chat_data.append(metric.chat_messages)
            else:
                agent_data.append(0)
                flow_data.append(0)
                chat_data.append(0)
            
            current_date += timedelta(days=1)
        
        return ChartData(
            labels=labels,
            datasets=[
                {
                    "label": "Execuções de Agentes",
                    "data": agent_data,
                    "borderColor": "#3B82F6",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)"
                },
                {
                    "label": "Execuções de Flows",
                    "data": flow_data,
                    "borderColor": "#10B981",
                    "backgroundColor": "rgba(16, 185, 129, 0.1)"
                },
                {
                    "label": "Mensagens de Chat",
                    "data": chat_data,
                    "borderColor": "#F59E0B",
                    "backgroundColor": "rgba(245, 158, 11, 0.1)"
                }
            ]
        )
    
    def _get_time_saved_chart(self, user_id: int, days: int = 30) -> ChartData:
        """Gera dados do gráfico de tempo economizado"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Buscar métricas diárias
        metrics = self.db.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date >= start_date,
                UserMetrics.metric_date <= end_date
            )
        ).order_by(UserMetrics.metric_date).all()
        
        # Criar dados para o gráfico
        labels = []
        time_data = []
        cumulative_data = []
        cumulative_total = 0.0
        
        # Preencher todos os dias
        current_date = start_date
        metrics_dict = {m.metric_date: m for m in metrics}
        
        while current_date <= end_date:
            labels.append(current_date.strftime("%d/%m"))
            
            metric = metrics_dict.get(current_date)
            daily_time = metric.time_saved if metric else 0.0
            
            time_data.append(daily_time)
            cumulative_total += daily_time
            cumulative_data.append(cumulative_total)
            
            current_date += timedelta(days=1)
        
        return ChartData(
            labels=labels,
            datasets=[
                {
                    "label": "Tempo Economizado (horas)",
                    "data": time_data,
                    "borderColor": "#8B5CF6",
                    "backgroundColor": "rgba(139, 92, 246, 0.1)",
                    "type": "bar"
                },
                {
                    "label": "Total Acumulado (horas)",
                    "data": cumulative_data,
                    "borderColor": "#EF4444",
                    "backgroundColor": "rgba(239, 68, 68, 0.1)",
                    "type": "line"
                }
            ]
        )
    
    def update_user_metrics(self, user_id: int, metric_date: Optional[date] = None) -> bool:
        """
        Atualiza métricas do usuário para uma data específica
        
        Args:
            user_id: ID do usuário
            metric_date: Data das métricas (padrão: hoje)
            
        Returns:
            True se atualizado com sucesso
        """
        if metric_date is None:
            metric_date = date.today()
        
        # Buscar ou criar métrica
        metric = self.db.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date == metric_date
            )
        ).first()
        
        if not metric:
            metric = UserMetrics(
                user_id=user_id,
                metric_date=metric_date
            )
            self.db.add(metric)
        
        # Contar agentes
        metric.total_agents = self.db.query(Agent).filter(Agent.user_id == user_id).count()
        
        # Contar flows
        metric.total_flows = self.db.query(Flow).filter(Flow.user_id == user_id).count()
        
        # Contar execuções do dia
        metric.agent_executions = self.db.query(AgentExecutionDB).filter(
            and_(
                AgentExecutionDB.user_id == user_id,
                func.date(AgentExecutionDB.created_at) == metric_date
            )
        ).count()
        
        metric.flow_executions = self.db.query(FlowExecution).filter(
            and_(
                FlowExecution.user_id == user_id,
                func.date(FlowExecution.started_at) == metric_date
            )
        ).count()
        
        # Contar uploads do dia
        metric.file_uploads = self.db.query(File).filter(
            and_(
                File.user_id == user_id,
                func.date(File.created_at) == metric_date
            )
        ).count()
        
        # Contar mensagens do dia
        metric.chat_messages = self.db.query(Message).filter(
            and_(
                Message.user_id == user_id,
                func.date(Message.created_at) == metric_date
            )
        ).count()
        
        # Calcular tempo economizado (estimativa)
        # Cada execução de agente economiza ~5 minutos
        # Cada execução de flow economiza ~30 minutos
        time_saved_hours = (metric.agent_executions * 5 + metric.flow_executions * 30) / 60.0
        metric.time_saved = time_saved_hours
        
        metric.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def get_usage_metrics(self, user_id: int, start_date: date, end_date: date) -> List[UsageMetrics]:
        """
        Busca métricas de uso por período
        
        Args:
            user_id: ID do usuário
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de métricas
        """
        metrics = self.db.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date >= start_date,
                UserMetrics.metric_date <= end_date
            )
        ).order_by(UserMetrics.metric_date).all()
        
        return [
            UsageMetrics(
                date=metric.metric_date,
                agent_executions=metric.agent_executions,
                flow_executions=metric.flow_executions,
                file_uploads=metric.file_uploads,
                chat_messages=metric.chat_messages,
                time_saved=metric.time_saved
            )
            for metric in metrics
        ]

