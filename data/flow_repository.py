"""
Repositório de flows/automações para o sistema EmployeeVirtual
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_

from data.entities import (
    FlowEntity, FlowStepEntity, FlowExecutionEntity, FlowExecutionStepEntity, FlowTemplateEntity
)
from models.flow_models import (
    FlowStatus, ExecutionStatus, StepType
)


class FlowRepository:
    """Repositório para operações de dados de flows/automações"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD Flows
    def create_flow(self, user_id: int, name: str, description: str = None, 
                   config: Dict[str, Any] = None) -> FlowEntity:
        """Cria um novo FlowEntity"""
        db_flow = FlowEntity(
            user_id=user_id,
            name=name,
            description=description,
            config=config or {}
        )
        self.db.add(db_flow)
        self.db.commit()
        self.db.refresh(db_flow)
        return db_flow
    
    def get_flow_by_id(self, flow_id: int, user_id: int = None) -> Optional[FlowEntity]:
        """Busca FlowEntity por ID"""
        query = self.db.query(FlowEntity).filter(FlowEntity.id == flow_id)
        if user_id:
            query = query.filter(FlowEntity.user_id == user_id)
        return query.first()
    
    def get_user_flows(self, user_id: int, skip: int = 0, limit: int = 50, 
                      status: FlowStatus = None) -> List[FlowEntity]:
        """Busca flows do usuário"""
        query = self.db.query(FlowEntity).filter(FlowEntity.user_id == user_id)
        
        if status:
            query = query.filter(FlowEntity.status == status)
        
        return query.order_by(desc(FlowEntity.updated_at)).offset(skip).limit(limit).all()
    
    def get_flow_by_name(self, user_id: int, name: str) -> Optional[FlowEntity]:
        """Busca FlowEntity por nome"""
        return self.db.query(FlowEntity).filter(
            and_(FlowEntity.user_id == user_id, FlowEntity.name == name)
        ).first()
    
    def update_flow(self, flow_id: int, user_id: int, **kwargs) -> Optional[FlowEntity]:
        """Atualiza dados do FlowEntity"""
        FlowEntity = self.get_flow_by_id(flow_id, user_id)
        if not FlowEntity:
            return None
        
        for key, value in kwargs.items():
            if hasattr(FlowEntity, key) and value is not None:
                setattr(FlowEntity, key, value)
        
        FlowEntity.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(FlowEntity)
        return FlowEntity
    
    def delete_flow(self, flow_id: int, user_id: int) -> bool:
        """Remove FlowEntity"""
        FlowEntity = self.get_flow_by_id(flow_id, user_id)
        if not FlowEntity:
            return False
        
        # Remover execuções relacionadas
        self.db.query(FlowExecutionStepEntity).join(FlowExecutionEntity).filter(
            FlowExecutionEntity.flow_id == flow_id
        ).delete()
        
        self.db.query(FlowExecutionEntity).filter(FlowExecutionEntity.flow_id == flow_id).delete()
        
        # Remover etapas relacionadas
        self.db.query(FlowStepEntity).filter(FlowStepEntity.flow_id == flow_id).delete()
        
        # Remover FlowEntity
        self.db.delete(FlowEntity)
        self.db.commit()
        return True
    
    def get_flows_count(self, user_id: int, status: FlowStatus = None) -> int:
        """Retorna contagem de flows"""
        query = self.db.query(FlowEntity).filter(FlowEntity.user_id == user_id)
        if status:
            query = query.filter(FlowEntity.status == status)
        return query.count()
    
    def activate_flow(self, flow_id: int, user_id: int) -> bool:
        """Ativa um FlowEntity"""
        return self.update_flow(flow_id, user_id, status=FlowStatus.ACTIVE) is not None
    
    def deactivate_flow(self, flow_id: int, user_id: int) -> bool:
        """Desativa um FlowEntity"""
        return self.update_flow(flow_id, user_id, status=FlowStatus.INACTIVE) is not None
    
    def pause_flow(self, flow_id: int, user_id: int) -> bool:
        """Pausa um FlowEntity"""
        return self.update_flow(flow_id, user_id, status=FlowStatus.PAUSED) is not None
    
    # CRUD Etapas de FlowEntity
    def create_flow_step(self, flow_id: int, name: str, step_type: StepType, 
                        order: int, description: str = None, 
                        config: Dict[str, Any] = None) -> FlowStepEntity:
        """Cria uma etapa do FlowEntity"""
        db_step = FlowStepEntity(
            flow_id=flow_id,
            name=name,
            step_type=step_type,
            order=order,
            description=description,
            config=config or {}
        )
        self.db.add(db_step)
        self.db.commit()
        self.db.refresh(db_step)
        return db_step
    
    def get_flow_steps(self, flow_id: int) -> List[FlowStepEntity]:
        """Busca etapas de um FlowEntity"""
        return self.db.query(FlowStepEntity).filter(
            FlowStepEntity.flow_id == flow_id
        ).order_by(FlowStepEntity.order).all()
    
    def get_flow_step_by_id(self, step_id: int) -> Optional[FlowStepEntity]:
        """Busca etapa por ID"""
        return self.db.query(FlowStepEntity).filter(FlowStepEntity.id == step_id).first()
    
    def update_flow_step(self, step_id: int, **kwargs) -> Optional[FlowStepEntity]:
        """Atualiza etapa do FlowEntity"""
        step = self.get_flow_step_by_id(step_id)
        if not step:
            return None
        
        for key, value in kwargs.items():
            if hasattr(step, key) and value is not None:
                setattr(step, key, value)
        
        step.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(step)
        return step
    
    def delete_flow_step(self, step_id: int) -> bool:
        """Remove etapa do FlowEntity"""
        step = self.get_flow_step_by_id(step_id)
        if not step:
            return False
        
        self.db.delete(step)
        self.db.commit()
        return True
    
    def reorder_flow_steps(self, flow_id: int, step_orders: List[Dict[str, int]]) -> bool:
        """Reordena etapas do FlowEntity"""
        try:
            for step_order in step_orders:
                step_id = step_order.get('step_id')
                new_order = step_order.get('order')
                
                step = self.db.query(FlowStepEntity).filter(
                    and_(FlowStepEntity.id == step_id, FlowStepEntity.flow_id == flow_id)
                ).first()
                
                if step:
                    step.order = new_order
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    # CRUD Execuções de FlowEntity
    def create_flow_execution(self, flow_id: int, user_id: int, 
                             trigger_data: Dict[str, Any] = None) -> FlowExecutionEntity:
        """Cria uma execução de FlowEntity"""
        db_execution = FlowExecutionEntity(
            flow_id=flow_id,
            user_id=user_id,
            trigger_data=trigger_data or {}
        )
        self.db.add(db_execution)
        self.db.commit()
        self.db.refresh(db_execution)
        return db_execution
    
    def get_flow_execution_by_id(self, execution_id: int) -> Optional[FlowExecutionEntity]:
        """Busca execução por ID"""
        return self.db.query(FlowExecutionEntity).filter(FlowExecutionEntity.id == execution_id).first()
    
    def get_flow_executions(self, flow_id: int = None, user_id: int = None, 
                           skip: int = 0, limit: int = 50, 
                           status: ExecutionStatus = None) -> List[FlowExecutionEntity]:
        """Busca execuções de FlowEntity"""
        query = self.db.query(FlowExecutionEntity)
        
        if flow_id:
            query = query.filter(FlowExecutionEntity.flow_id == flow_id)
        
        if user_id:
            query = query.filter(FlowExecutionEntity.user_id == user_id)
        
        if status:
            query = query.filter(FlowExecutionEntity.status == status)
        
        return query.order_by(desc(FlowExecutionEntity.created_at)).offset(skip).limit(limit).all()
    
    def update_flow_execution(self, execution_id: int, **kwargs) -> Optional[FlowExecutionEntity]:
        """Atualiza execução de FlowEntity"""
        execution = self.get_flow_execution_by_id(execution_id)
        if not execution:
            return None
        
        for key, value in kwargs.items():
            if hasattr(execution, key) and value is not None:
                setattr(execution, key, value)
        
        if 'status' in kwargs and kwargs['status'] in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            execution.ended_at = datetime.utcnow()
            if execution.started_at:
                execution.duration = (execution.ended_at - execution.started_at).total_seconds()
        
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def start_flow_execution(self, execution_id: int) -> bool:
        """Inicia execução de FlowEntity"""
        execution = self.get_flow_execution_by_id(execution_id)
        if not execution:
            return False
        
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def complete_flow_execution(self, execution_id: int, result: Dict[str, Any] = None) -> bool:
        """Completa execução de FlowEntity"""
        execution = self.get_flow_execution_by_id(execution_id)
        if not execution:
            return False
        
        execution.status = ExecutionStatus.COMPLETED
        execution.ended_at = datetime.utcnow()
        execution.result = result or {}
        
        if execution.started_at:
            execution.duration = (execution.ended_at - execution.started_at).total_seconds()
        
        self.db.commit()
        return True
    
    def fail_flow_execution(self, execution_id: int, error_message: str = None) -> bool:
        """Marca execução como falha"""
        execution = self.get_flow_execution_by_id(execution_id)
        if not execution:
            return False
        
        execution.status = ExecutionStatus.FAILED
        execution.ended_at = datetime.utcnow()
        execution.error_message = error_message
        
        if execution.started_at:
            execution.duration = (execution.ended_at - execution.started_at).total_seconds()
        
        self.db.commit()
        return True
    
    # CRUD Etapas de Execução
    def create_execution_step(self, execution_id: int, step_id: int, 
                             input_data: Dict[str, Any] = None) -> FlowExecutionStepEntity:
        """Cria uma etapa de execução"""
        db_execution_step = FlowExecutionStepEntity(
            execution_id=execution_id,
            step_id=step_id,
            input_data=input_data or {}
        )
        self.db.add(db_execution_step)
        self.db.commit()
        self.db.refresh(db_execution_step)
        return db_execution_step
    
    def get_execution_steps(self, execution_id: int) -> List[FlowExecutionStepEntity]:
        """Busca etapas de uma execução"""
        return self.db.query(FlowExecutionStepEntity).filter(
            FlowExecutionStepEntity.execution_id == execution_id
        ).order_by(FlowExecutionStepEntity.created_at).all()
    
    def update_execution_step(self, execution_step_id: int, **kwargs) -> Optional[FlowExecutionStepEntity]:
        """Atualiza etapa de execução"""
        execution_step = self.db.query(FlowExecutionStepEntity).filter(
            FlowExecutionStepEntity.id == execution_step_id
        ).first()
        
        if not execution_step:
            return None
        
        for key, value in kwargs.items():
            if hasattr(execution_step, key) and value is not None:
                setattr(execution_step, key, value)
        
        if 'status' in kwargs and kwargs['status'] in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            execution_step.ended_at = datetime.utcnow()
            if execution_step.started_at:
                execution_step.duration = (execution_step.ended_at - execution_step.started_at).total_seconds()
        
        self.db.commit()
        self.db.refresh(execution_step)
        return execution_step
    
    # Estatísticas e relatórios
    def get_flow_statistics(self, flow_id: int) -> Dict[str, Any]:
        """Busca estatísticas de um FlowEntity"""
        FlowEntity = self.get_flow_by_id(flow_id)
        if not FlowEntity:
            return {}
        
        # Contagem de execuções por status
        execution_stats = self.db.query(
            FlowExecutionEntity.status,
            func.count(FlowExecutionEntity.id).label('count')
        ).filter(FlowExecutionEntity.flow_id == flow_id).group_by(FlowExecutionEntity.status).all()
        
        execution_counts = {stat.status: stat.count for stat in execution_stats}
        
        # Duração média
        avg_duration = self.db.query(
            func.avg(FlowExecutionEntity.duration)
        ).filter(
            and_(
                FlowExecutionEntity.flow_id == flow_id,
                FlowExecutionEntity.duration.isnot(None)
            )
        ).scalar() or 0
        
        # Tempo total economizado
        total_time_saved = self.db.query(
            func.sum(FlowExecutionEntity.time_saved)
        ).filter(
            and_(
                FlowExecutionEntity.flow_id == flow_id,
                FlowExecutionEntity.time_saved.isnot(None)
            )
        ).scalar() or 0
        
        # Última execução
        last_execution = self.db.query(FlowExecutionEntity).filter(
            FlowExecutionEntity.flow_id == flow_id
        ).order_by(desc(FlowExecutionEntity.created_at)).first()
        
        return {
            'flow_id': flow_id,
            'flow_name': FlowEntity.name,
            'status': FlowEntity.status,
            'execution_counts': execution_counts,
            'total_executions': sum(execution_counts.values()),
            'avg_duration_seconds': float(avg_duration),
            'total_time_saved_hours': float(total_time_saved),
            'last_execution_at': last_execution.created_at if last_execution else None,
            'success_rate': (
                execution_counts.get(ExecutionStatus.COMPLETED, 0) / 
                max(sum(execution_counts.values()), 1) * 100
            )
        }
    
    def get_user_flow_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Busca métricas de flows do usuário"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Contagem de flows por status
        flow_counts = self.db.query(
            FlowEntity.status,
            func.count(FlowEntity.id).label('count')
        ).filter(FlowEntity.user_id == user_id).group_by(FlowEntity.status).all()
        
        flow_status_counts = {stat.status: stat.count for stat in flow_counts}
        
        # Execuções no período
        executions_in_period = self.db.query(FlowExecutionEntity).join(FlowEntity).filter(
            and_(
                FlowEntity.user_id == user_id,
                FlowExecutionEntity.created_at >= since_date
            )
        ).count()
        
        # Execuções bem-sucedidas
        successful_executions = self.db.query(FlowExecutionEntity).join(FlowEntity).filter(
            and_(
                FlowEntity.user_id == user_id,
                FlowExecutionEntity.status == ExecutionStatus.COMPLETED,
                FlowExecutionEntity.created_at >= since_date
            )
        ).count()
        
        # Tempo total economizado
        total_time_saved = self.db.query(
            func.sum(FlowExecutionEntity.time_saved)
        ).join(FlowEntity).filter(
            and_(
                FlowEntity.user_id == user_id,
                FlowExecutionEntity.created_at >= since_date,
                FlowExecutionEntity.time_saved.isnot(None)
            )
        ).scalar() or 0
        
        return {
            'user_id': user_id,
            'period_days': days,
            'flow_status_counts': flow_status_counts,
            'total_flows': sum(flow_status_counts.values()),
            'executions_in_period': executions_in_period,
            'successful_executions': successful_executions,
            'success_rate': (
                successful_executions / max(executions_in_period, 1) * 100
            ),
            'total_time_saved_hours': float(total_time_saved)
        }
    
    def get_active_flows(self, user_id: int) -> List[FlowEntity]:
        """Busca flows ativos do usuário"""
        return self.db.query(FlowEntity).filter(
            and_(FlowEntity.user_id == user_id, FlowEntity.status == FlowStatus.ACTIVE)
        ).order_by(desc(FlowEntity.updated_at)).all()
    
    def get_running_executions(self, user_id: int = None) -> List[FlowExecutionEntity]:
        """Busca execuções em andamento"""
        query = self.db.query(FlowExecutionEntity).filter(
            FlowExecutionEntity.status == ExecutionStatus.RUNNING
        )
        
        if user_id:
            query = query.filter(FlowExecutionEntity.user_id == user_id)
        
        return query.order_by(FlowExecutionEntity.started_at).all()
    
    def search_flows(self, user_id: int, query: str, status: FlowStatus = None, 
                    limit: int = 50) -> List[FlowEntity]:
        """Busca flows por texto"""
        db_query = self.db.query(FlowEntity).filter(FlowEntity.user_id == user_id)
        
        if query:
            db_query = db_query.filter(
                or_(
                    FlowEntity.name.ilike(f"%{query}%"),
                    FlowEntity.description.ilike(f"%{query}%")
                )
            )
        
        if status:
            db_query = db_query.filter(FlowEntity.status == status)
        
        return db_query.order_by(desc(FlowEntity.updated_at)).limit(limit).all()
