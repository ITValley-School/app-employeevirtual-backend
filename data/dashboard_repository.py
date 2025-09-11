"""
Repositório de dashboard e métricas para o sistema EmployeeVirtual
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text

from models.dashboard_models import MetricType, PeriodType
from data.entities.agent_entities import AgentEntity, AgentExecutionEntity
from data.entities.flow_entities import FlowEntity, FlowExecutionEntity
from data.entities.file_entities import DataLakeFileEntity
from data.entities.chat_entities import MessageEntity, ConversationEntity
from data.entities.user_entities import UserEntity, UserActivityEntity
from models.agent_models import AgentStatus
from models.flow_models import FlowStatus
from models.chat_models import MessageType


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
        total_agents = self.db.query(AgentEntity).filter(AgentEntity.user_id == user_id).count()
        
        # Contagem de flows
        total_flows = self.db.query(FlowEntity).filter(FlowEntity.user_id == user_id).count()
        active_flows = self.db.query(FlowEntity).filter(
            and_(FlowEntity.user_id == user_id, FlowEntity.status == FlowStatus.ACTIVE)
        ).count()
        paused_flows = self.db.query(FlowEntity).filter(
            and_(FlowEntity.user_id == user_id, FlowEntity.status == FlowStatus.PAUSED)
        ).count()
        error_flows = self.db.query(FlowEntity).filter(
            and_(FlowEntity.user_id == user_id, FlowEntity.status == FlowStatus.ERROR)
        ).count()
        draft_flows = self.db.query(FlowEntity).filter(
            and_(FlowEntity.user_id == user_id, FlowEntity.status == FlowStatus.DRAFT)
        ).count()
        
        # Execuções de agentes
        executions_today = self.db.query(AgentExecutionEntity).join(AgentEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                AgentExecutionEntity.created_at >= today_start
            )
        ).count()
        
        executions_all_time = self.db.query(AgentExecutionEntity).join(AgentEntity).filter(
            AgentEntity.user_id == user_id
        ).count()
        
        # Tempo economizado (baseado nas execuções)
        time_saved_today = self.db.query(
            func.sum(AgentExecutionEntity.time_saved)
        ).join(AgentEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                AgentExecutionEntity.created_at >= today_start,
                AgentExecutionEntity.time_saved.isnot(None)
            )
        ).scalar() or 0.0
        
        time_saved_all_time = self.db.query(
            func.sum(AgentExecutionEntity.time_saved)
        ).join(AgentEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                AgentExecutionEntity.time_saved.isnot(None)
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
            AgentEntity.id,
            AgentEntity.name,
            func.count(AgentExecutionEntity.id).label('total_executions'),
            func.sum(
                func.case(
                    [(AgentExecutionEntity.created_at >= today_start, 1)],
                    else_=0
                )
            ).label('executions_today'),
            func.sum(
                func.case(
                    [(AgentExecutionEntity.created_at >= week_start, 1)],
                    else_=0
                )
            ).label('executions_this_week'),
            func.avg(AgentExecutionEntity.duration).label('avg_duration'),
            func.sum(AgentExecutionEntity.time_saved).label('total_time_saved'),
            func.sum(
                func.case(
                    [(AgentExecutionEntity.status == 'success', 1)],
                    else_=0
                )
            ).label('successful_executions'),
            func.sum(
                func.case(
                    [(AgentExecutionEntity.status == 'error', 1)],
                    else_=0
                )
            ).label('failed_executions')
        ).outerjoin(AgentExecutionEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                or_(AgentExecutionEntity.created_at >= since_date, AgentExecutionEntity.id.is_(None))
            )
        ).group_by(AgentEntity.id, AgentEntity.name)
        
        if agent_id:
            query = query.filter(AgentEntity.id == agent_id)
        
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
            FlowEntity.id,
            FlowEntity.name,
            FlowEntity.status,
            func.count(FlowExecutionEntity.id).label('total_executions'),
            func.avg(FlowExecutionEntity.duration).label('avg_duration'),
            func.sum(FlowExecutionEntity.time_saved).label('total_time_saved'),
            func.sum(
                func.case(
                    [(FlowExecutionEntity.status == 'success', 1)],
                    else_=0
                )
            ).label('successful_executions'),
            func.sum(
                func.case(
                    [(FlowExecutionEntity.status == 'error', 1)],
                    else_=0
                )
            ).label('failed_executions')
        ).outerjoin(FlowExecutionEntity).filter(
            and_(
                FlowEntity.user_id == user_id,
                or_(FlowExecutionEntity.created_at >= since_date, FlowExecutionEntity.id.is_(None))
            )
        ).group_by(FlowEntity.id, FlowEntity.name, FlowEntity.status)
        
        if flow_id:
            query = query.filter(FlowEntity.id == flow_id)
        
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
                func.date(AgentExecutionEntity.created_at).label('date'),
                func.count(AgentExecutionEntity.id).label('count'),
                func.sum(AgentExecutionEntity.time_saved).label('time_saved')
            ).join(AgentEntity).filter(
                and_(
                    AgentEntity.user_id == user_id,
                    AgentExecutionEntity.created_at >= since_date
                )
            ).group_by(func.date(AgentExecutionEntity.created_at)).order_by('date').all()
            
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
            func.date_trunc('week', AgentExecutionEntity.created_at).label('week_start'),
            func.count(AgentExecutionEntity.id).label('executions'),
            func.sum(AgentExecutionEntity.time_saved).label('time_saved')
        ).join(AgentEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                AgentExecutionEntity.created_at >= since_date
            )
        ).group_by(func.date_trunc('week', AgentExecutionEntity.created_at)).order_by('week_start').all()
        
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
        total_files = self.db.query(DataLakeFileEntity).filter(DataLakeFileEntity.user_id == user_id).count()
        
        # Arquivos novos no período
        new_files = self.db.query(DataLakeFileEntity).filter(
            and_(
                DataLakeFileEntity.user_id == user_id,
                DataLakeFileEntity.created_at >= since_date
            )
        ).count()
        
        # Tamanho total dos arquivos
        total_size = self.db.query(
            func.sum(DataLakeFileEntity.file_size)
        ).filter(DataLakeFileEntity.user_id == user_id).scalar() or 0
        
        # Arquivos por tipo
        file_types = self.db.query(
            DataLakeFileEntity.file_type,
            func.count(DataLakeFileEntity.id).label('count')
        ).filter(DataLakeFileEntity.user_id == user_id).group_by(DataLakeFileEntity.file_type).all()
        
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
        active_conversations = self.db.query(ConversationEntity).filter(
            and_(
                ConversationEntity.user_id == user_id,
                ConversationEntity.status == 'active'
            )
        ).count()
        
        # Mensagens no período
        messages_sent = self.db.query(MessageEntity).join(ConversationEntity).filter(
            and_(
                ConversationEntity.user_id == user_id,
                MessageEntity.message_type == MessageType.UserEntity,
                MessageEntity.created_at >= since_date
            )
        ).count()
        
        messages_received = self.db.query(MessageEntity).join(ConversationEntity).filter(
            and_(
                ConversationEntity.user_id == user_id,
                MessageEntity.message_type == MessageType.AgentEntity,
                MessageEntity.created_at >= since_date
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
        UserEntity = self.db.query(UserEntity).filter(UserEntity.id == user_id).first()
        if not UserEntity:
            return {}
        
        # Atividades recentes
        recent_activities = self.db.query(
            UserActivityEntity.activity_type,
            func.count(UserActivityEntity.id).label('count')
        ).filter(
            and_(
                UserActivityEntity.user_id == user_id,
                UserActivityEntity.created_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).group_by(UserActivityEntity.activity_type).all()
        
        activity_summary = {activity.activity_type: activity.count for activity in recent_activities}
        
        return {
            'user_id': user_id,
            'name': UserEntity.name,
            'email': UserEntity.email,
            'plan': UserEntity.plan,
            'created_at': UserEntity.created_at,
            'last_login': UserEntity.last_login,
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
            AgentEntity.name,
            func.count(AgentExecutionEntity.id).label('executions')
        ).join(AgentExecutionEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                AgentExecutionEntity.created_at >= since_date
            )
        ).group_by(AgentEntity.id, AgentEntity.name).order_by(desc('executions')).limit(10).all()
        
        # Tempo total economizado
        total_time_saved = self.db.query(
            func.sum(AgentExecutionEntity.time_saved)
        ).join(AgentEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                AgentExecutionEntity.created_at >= since_date,
                AgentExecutionEntity.time_saved.isnot(None)
            )
        ).scalar() or 0.0
        
        # Taxa de sucesso geral
        success_rate = self.db.query(
            func.avg(
                func.case(
                    [(AgentExecutionEntity.status == 'success', 100.0)],
                    else_=0.0
                )
            )
        ).join(AgentEntity).filter(
            and_(
                AgentEntity.user_id == user_id,
                AgentExecutionEntity.created_at >= since_date
            )
        ).scalar() or 0.0
        
        return {
            'period_days': days,
            'total_time_saved_hours': float(total_time_saved),
            'average_success_rate': float(success_rate),
            'top_agents': [
                {'name': AgentEntity.name, 'executions': AgentEntity.executions}
                for AgentEntity in top_agents
            ],
            'dashboard_summary': self.get_dashboard_summary(user_id)
        }
