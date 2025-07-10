"""
Repositório de dashboard e métricas para o sistema EmployeeVirtual
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text

from models.dashboard_models import MetricType, PeriodType
from models.agent_models import Agent, AgentExecutionDB
from models.flow_models import Flow, FlowExecution, FlowStatus
from models.file_models import DataLakeFile
from models.chat_models import Message, Conversation, MessageType
from models.user_models import User, UserActivity


class DashboardRepository:
    """Repositório para operações de dados de dashboard e métricas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Métricas gerais do dashboard
    def get_dashboard_summary(self, user_id: int) -> Dict[str, Any]:
        """Busca resumo geral do dashboard"""
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Contagem de agentes
        total_agents = self.db.query(Agent).filter(Agent.user_id == user_id).count()
        
        # Contagem de flows
        total_flows = self.db.query(Flow).filter(Flow.user_id == user_id).count()
        active_flows = self.db.query(Flow).filter(
            and_(Flow.user_id == user_id, Flow.status == FlowStatus.ACTIVE)
        ).count()
        paused_flows = self.db.query(Flow).filter(
            and_(Flow.user_id == user_id, Flow.status == FlowStatus.PAUSED)
        ).count()
        error_flows = self.db.query(Flow).filter(
            and_(Flow.user_id == user_id, Flow.status == FlowStatus.ERROR)
        ).count()
        draft_flows = self.db.query(Flow).filter(
            and_(Flow.user_id == user_id, Flow.status == FlowStatus.DRAFT)
        ).count()
        
        # Execuções de agentes
        executions_today = self.db.query(AgentExecutionDB).join(Agent).filter(
            and_(
                Agent.user_id == user_id,
                AgentExecutionDB.created_at >= today_start
            )
        ).count()
        
        executions_all_time = self.db.query(AgentExecutionDB).join(Agent).filter(
            Agent.user_id == user_id
        ).count()
        
        # Tempo economizado (baseado nas execuções)
        time_saved_today = self.db.query(
            func.sum(AgentExecutionDB.time_saved)
        ).join(Agent).filter(
            and_(
                Agent.user_id == user_id,
                AgentExecutionDB.created_at >= today_start,
                AgentExecutionDB.time_saved.isnot(None)
            )
        ).scalar() or 0.0
        
        time_saved_all_time = self.db.query(
            func.sum(AgentExecutionDB.time_saved)
        ).join(Agent).filter(
            and_(
                Agent.user_id == user_id,
                AgentExecutionDB.time_saved.isnot(None)
            )
        ).scalar() or 0.0
        
        return {
            'total_agents': total_agents,
            'total_flows': total_flows,
            'total_executions_today': executions_today,
            'total_executions_all_time': executions_all_time,
            'active_flows': active_flows,
            'paused_flows': paused_flows,
            'error_flows': error_flows,
            'draft_flows': draft_flows,
            'time_saved_today': float(time_saved_today),
            'time_saved_all_time': float(time_saved_all_time)
        }
    
    # Métricas de agentes
    def get_agent_metrics(self, user_id: int, agent_id: int = None, days: int = 30) -> List[Dict[str, Any]]:
        """Busca métricas de agentes"""
        since_date = datetime.utcnow() - timedelta(days=days)
        today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        week_start = datetime.utcnow() - timedelta(days=7)
        
        query = self.db.query(
            Agent.id,
            Agent.name,
            func.count(AgentExecutionDB.id).label('total_executions'),
            func.sum(
                func.case(
                    [(AgentExecutionDB.created_at >= today_start, 1)],
                    else_=0
                )
            ).label('executions_today'),
            func.sum(
                func.case(
                    [(AgentExecutionDB.created_at >= week_start, 1)],
                    else_=0
                )
            ).label('executions_this_week'),
            func.avg(AgentExecutionDB.duration).label('avg_duration'),
            func.sum(AgentExecutionDB.time_saved).label('total_time_saved'),
            func.sum(
                func.case(
                    [(AgentExecutionDB.status == 'success', 1)],
                    else_=0
                )
            ).label('successful_executions'),
            func.sum(
                func.case(
                    [(AgentExecutionDB.status == 'error', 1)],
                    else_=0
                )
            ).label('failed_executions')
        ).outerjoin(AgentExecutionDB).filter(
            and_(
                Agent.user_id == user_id,
                or_(AgentExecutionDB.created_at >= since_date, AgentExecutionDB.id.is_(None))
            )
        ).group_by(Agent.id, Agent.name)
        
        if agent_id:
            query = query.filter(Agent.id == agent_id)
        
        results = query.all()
        
        return [
            {
                'agent_id': result.id,
                'agent_name': result.name,
                'total_executions': result.total_executions or 0,
                'executions_today': result.executions_today or 0,
                'executions_this_week': result.executions_this_week or 0,
                'avg_duration': float(result.avg_duration or 0),
                'total_time_saved': float(result.total_time_saved or 0),
                'successful_executions': result.successful_executions or 0,
                'failed_executions': result.failed_executions or 0,
                'success_rate': (
                    (result.successful_executions or 0) / max(result.total_executions or 1, 1) * 100
                )
            }
            for result in results
        ]
    
    # Métricas de flows
    def get_flow_metrics(self, user_id: int, flow_id: int = None, days: int = 30) -> List[Dict[str, Any]]:
        """Busca métricas de flows"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(
            Flow.id,
            Flow.name,
            Flow.status,
            func.count(FlowExecution.id).label('total_executions'),
            func.avg(FlowExecution.duration).label('avg_duration'),
            func.sum(FlowExecution.time_saved).label('total_time_saved'),
            func.sum(
                func.case(
                    [(FlowExecution.status == 'success', 1)],
                    else_=0
                )
            ).label('successful_executions'),
            func.sum(
                func.case(
                    [(FlowExecution.status == 'error', 1)],
                    else_=0
                )
            ).label('failed_executions')
        ).outerjoin(FlowExecution).filter(
            and_(
                Flow.user_id == user_id,
                or_(FlowExecution.created_at >= since_date, FlowExecution.id.is_(None))
            )
        ).group_by(Flow.id, Flow.name, Flow.status)
        
        if flow_id:
            query = query.filter(Flow.id == flow_id)
        
        results = query.all()
        
        return [
            {
                'flow_id': result.id,
                'flow_name': result.name,
                'status': result.status,
                'total_executions': result.total_executions or 0,
                'avg_duration': float(result.avg_duration or 0),
                'total_time_saved': float(result.total_time_saved or 0),
                'successful_executions': result.successful_executions or 0,
                'failed_executions': result.failed_executions or 0,
                'success_rate': (
                    (result.successful_executions or 0) / max(result.total_executions or 1, 1) * 100
                )
            }
            for result in results
        ]
    
    # Métricas temporais
    def get_daily_metrics(self, user_id: int, metric_type: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Busca métricas diárias"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        if metric_type == MetricType.AGENT_EXECUTION or metric_type is None:
            results = self.db.query(
                func.date(AgentExecutionDB.created_at).label('date'),
                func.count(AgentExecutionDB.id).label('count'),
                func.sum(AgentExecutionDB.time_saved).label('time_saved')
            ).join(Agent).filter(
                and_(
                    Agent.user_id == user_id,
                    AgentExecutionDB.created_at >= since_date
                )
            ).group_by(func.date(AgentExecutionDB.created_at)).order_by('date').all()
            
            return [
                {
                    'date': result.date,
                    'metric_type': MetricType.AGENT_EXECUTION,
                    'count': result.count,
                    'time_saved': float(result.time_saved or 0)
                }
                for result in results
            ]
        
        return []
    
    def get_weekly_metrics(self, user_id: int, weeks: int = 12) -> List[Dict[str, Any]]:
        """Busca métricas semanais"""
        since_date = datetime.utcnow() - timedelta(weeks=weeks)
        
        results = self.db.query(
            func.date_trunc('week', AgentExecutionDB.created_at).label('week_start'),
            func.count(AgentExecutionDB.id).label('executions'),
            func.sum(AgentExecutionDB.time_saved).label('time_saved')
        ).join(Agent).filter(
            and_(
                Agent.user_id == user_id,
                AgentExecutionDB.created_at >= since_date
            )
        ).group_by(func.date_trunc('week', AgentExecutionDB.created_at)).order_by('week_start').all()
        
        return [
            {
                'week_start': result.week_start,
                'executions': result.executions,
                'time_saved': float(result.time_saved or 0)
            }
            for result in results
        ]
    
    # Métricas de arquivos
    def get_file_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Busca métricas de arquivos"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Total de arquivos
        total_files = self.db.query(DataLakeFile).filter(DataLakeFile.user_id == user_id).count()
        
        # Arquivos novos no período
        new_files = self.db.query(DataLakeFile).filter(
            and_(
                DataLakeFile.user_id == user_id,
                DataLakeFile.created_at >= since_date
            )
        ).count()
        
        # Tamanho total dos arquivos
        total_size = self.db.query(
            func.sum(DataLakeFile.file_size)
        ).filter(DataLakeFile.user_id == user_id).scalar() or 0
        
        # Arquivos por tipo
        file_types = self.db.query(
            DataLakeFile.file_type,
            func.count(DataLakeFile.id).label('count')
        ).filter(DataLakeFile.user_id == user_id).group_by(DataLakeFile.file_type).all()
        
        return {
            'total_files': total_files,
            'new_files_period': new_files,
            'total_size_bytes': int(total_size),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_types': {ft.file_type: ft.count for ft in file_types}
        }
    
    # Métricas de chat
    def get_chat_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Busca métricas de chat"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Conversações ativas
        active_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == 'active'
            )
        ).count()
        
        # Mensagens no período
        messages_sent = self.db.query(Message).join(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Message.message_type == MessageType.USER,
                Message.created_at >= since_date
            )
        ).count()
        
        messages_received = self.db.query(Message).join(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Message.message_type == MessageType.AGENT,
                Message.created_at >= since_date
            )
        ).count()
        
        return {
            'active_conversations': active_conversations,
            'messages_sent_period': messages_sent,
            'messages_received_period': messages_received,
            'total_messages_period': messages_sent + messages_received
        }
    
    # Métricas de usuário
    def get_user_metrics(self, user_id: int) -> Dict[str, Any]:
        """Busca métricas consolidadas do usuário"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Atividades recentes
        recent_activities = self.db.query(
            UserActivity.activity_type,
            func.count(UserActivity.id).label('count')
        ).filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.created_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).group_by(UserActivity.activity_type).all()
        
        activity_summary = {activity.activity_type: activity.count for activity in recent_activities}
        
        return {
            'user_id': user_id,
            'name': user.name,
            'email': user.email,
            'plan': user.plan,
            'created_at': user.created_at,
            'last_login': user.last_login,
            'activity_summary': activity_summary,
            'dashboard_summary': self.get_dashboard_summary(user_id),
            'file_metrics': self.get_file_metrics(user_id),
            'chat_metrics': self.get_chat_metrics(user_id)
        }
    
    # Relatórios
    def get_performance_report(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Gera relatório de performance"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Top agentes por execuções
        top_agents = self.db.query(
            Agent.name,
            func.count(AgentExecutionDB.id).label('executions')
        ).join(AgentExecutionDB).filter(
            and_(
                Agent.user_id == user_id,
                AgentExecutionDB.created_at >= since_date
            )
        ).group_by(Agent.id, Agent.name).order_by(desc('executions')).limit(10).all()
        
        # Tempo total economizado
        total_time_saved = self.db.query(
            func.sum(AgentExecutionDB.time_saved)
        ).join(Agent).filter(
            and_(
                Agent.user_id == user_id,
                AgentExecutionDB.created_at >= since_date,
                AgentExecutionDB.time_saved.isnot(None)
            )
        ).scalar() or 0.0
        
        # Taxa de sucesso geral
        success_rate = self.db.query(
            func.avg(
                func.case(
                    [(AgentExecutionDB.status == 'success', 100.0)],
                    else_=0.0
                )
            )
        ).join(Agent).filter(
            and_(
                Agent.user_id == user_id,
                AgentExecutionDB.created_at >= since_date
            )
        ).scalar() or 0.0
        
        return {
            'period_days': days,
            'total_time_saved_hours': float(total_time_saved),
            'average_success_rate': float(success_rate),
            'top_agents': [
                {'name': agent.name, 'executions': agent.executions}
                for agent in top_agents
            ],
            'dashboard_summary': self.get_dashboard_summary(user_id)
        }
