"""
Serviço de flows/automações para o sistema EmployeeVirtual
"""
import json
import time
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from models.flow_models import (
    Flow, FlowStep, FlowExecution, FlowExecutionStep, FlowTemplate,
    FlowCreate, FlowUpdate, FlowResponse, FlowExecutionRequest, FlowExecutionResponse,
    FlowStatus, ExecutionStatus, StepType
)
from models.user_models import UserActivity
from services.agent_service import AgentService
from services.orion_service import OrionService


class FlowService:
    """Serviço para gerenciamento de flows/automações"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService(db)
        self.orion_service = OrionService()
    
    def create_flow(self, user_id: int, flow_data: FlowCreate) -> FlowResponse:
        """
        Cria um novo flow
        
        Args:
            user_id: ID do usuário
            flow_data: Dados do flow
            
        Returns:
            FlowResponse: Dados do flow criado
        """
        # Criar flow
        db_flow = Flow(
            user_id=user_id,
            name=flow_data.name,
            description=flow_data.description,
            tags=json.dumps(flow_data.tags) if flow_data.tags else None,
            estimated_time=self._calculate_estimated_time(flow_data.steps)
        )
        
        self.db.add(db_flow)
        self.db.flush()  # Para obter o ID
        
        # Criar etapas
        for step_data in flow_data.steps:
            db_step = FlowStep(
                flow_id=db_flow.id,
                name=step_data.name,
                step_type=step_data.step_type,
                order=step_data.order,
                description=step_data.description,
                config=json.dumps(step_data.config) if step_data.config else None
            )
            self.db.add(db_step)
        
        self.db.commit()
        self.db.refresh(db_flow)
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "flow_created", 
            f"Flow '{flow_data.name}' criado com {len(flow_data.steps)} etapas"
        )
        
        return self._build_flow_response(db_flow)
    
    def get_user_flows(self, user_id: int) -> List[FlowResponse]:
        """
        Busca flows do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de flows
        """
        flows = self.db.query(Flow).filter(
            Flow.user_id == user_id
        ).order_by(desc(Flow.created_at)).all()
        
        return [self._build_flow_response(flow) for flow in flows]
    
    def get_flow_by_id(self, flow_id: int, user_id: Optional[int] = None) -> Optional[FlowResponse]:
        """
        Busca flow por ID
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário (para verificação de propriedade)
            
        Returns:
            FlowResponse ou None se não encontrado
        """
        query = self.db.query(Flow).filter(Flow.id == flow_id)
        
        if user_id:
            query = query.filter(Flow.user_id == user_id)
        
        flow = query.first()
        if not flow:
            return None
        
        return self._build_flow_response(flow)
    
    def update_flow(self, flow_id: int, user_id: int, flow_data: FlowUpdate) -> Optional[FlowResponse]:
        """
        Atualiza flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            flow_data: Dados a serem atualizados
            
        Returns:
            FlowResponse atualizado ou None se não encontrado
        """
        flow = self.db.query(Flow).filter(
            and_(Flow.id == flow_id, Flow.user_id == user_id)
        ).first()
        
        if not flow:
            return None
        
        # Atualizar campos fornecidos
        update_data = flow_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "tags" and value:
                setattr(flow, field, json.dumps(value))
            else:
                setattr(flow, field, value)
        
        flow.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(flow)
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "flow_updated", 
            f"Flow '{flow.name}' atualizado"
        )
        
        return self._build_flow_response(flow)
    
    def delete_flow(self, flow_id: int, user_id: int) -> bool:
        """
        Deleta flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            True se deletado com sucesso
        """
        flow = self.db.query(Flow).filter(
            and_(Flow.id == flow_id, Flow.user_id == user_id)
        ).first()
        
        if not flow:
            return False
        
        flow_name = flow.name
        
        # Deletar flow (cascade irá deletar relacionados)
        self.db.delete(flow)
        self.db.commit()
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "flow_deleted", 
            f"Flow '{flow_name}' deletado"
        )
        
        return True
    
    async def execute_flow(self, flow_id: int, user_id: int, execution_request: FlowExecutionRequest) -> FlowExecutionResponse:
        """
        Executa um flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            execution_request: Dados da execução
            
        Returns:
            Resultado da execução
        """
        flow = self.db.query(Flow).filter(
            and_(Flow.id == flow_id, Flow.user_id == user_id)
        ).first()
        
        if not flow:
            raise ValueError("Flow não encontrado")
        
        if flow.status != FlowStatus.ACTIVE:
            raise ValueError("Flow não está ativo")
        
        # Buscar etapas do flow
        steps = self.db.query(FlowStep).filter(
            FlowStep.flow_id == flow_id
        ).order_by(FlowStep.order).all()
        
        if not steps:
            raise ValueError("Flow não possui etapas")
        
        # Criar execução
        execution = FlowExecution(
            flow_id=flow_id,
            user_id=user_id,
            status=ExecutionStatus.RUNNING,
            input_data=json.dumps(execution_request.input_data),
            total_steps=len(steps),
            current_step=1
        )
        
        self.db.add(execution)
        self.db.flush()  # Para obter o ID
        
        start_time = time.time()
        
        try:
            # Executar etapas sequencialmente
            current_data = execution_request.input_data.copy()
            
            for i, step in enumerate(steps, 1):
                execution.current_step = i
                self.db.commit()
                
                # Executar etapa
                step_result = await self._execute_step(step, current_data, user_id)
                
                # Salvar resultado da etapa
                execution_step = FlowExecutionStep(
                    execution_id=execution.id,
                    step_id=step.id,
                    status=ExecutionStatus.COMPLETED if step_result["success"] else ExecutionStatus.FAILED,
                    input_data=json.dumps(current_data),
                    output_data=json.dumps(step_result["output"]) if step_result["success"] else None,
                    error_message=step_result.get("error_message"),
                    execution_time=step_result.get("execution_time"),
                    started_at=step_result.get("started_at"),
                    completed_at=datetime.utcnow()
                )
                
                self.db.add(execution_step)
                
                if not step_result["success"]:
                    # Falha na etapa
                    execution.status = ExecutionStatus.FAILED
                    execution.error_message = step_result.get("error_message")
                    break
                
                # Atualizar dados para próxima etapa
                if step_result["output"]:
                    current_data.update(step_result["output"])
                
                execution.completed_steps += 1
                
                # Verificar se deve pausar para revisão
                if step.step_type == StepType.PAUSE_FOR_REVIEW and not execution_request.auto_continue:
                    execution.status = ExecutionStatus.PAUSED
                    break
            
            # Finalizar execução se não pausou
            if execution.status == ExecutionStatus.RUNNING:
                execution.status = ExecutionStatus.COMPLETED
                execution.output_data = json.dumps(current_data)
            
            execution.execution_time = time.time() - start_time
            execution.completed_at = datetime.utcnow()
            
            # Atualizar estatísticas do flow
            flow.last_executed = datetime.utcnow()
            flow.execution_count += 1
            
            self.db.commit()
            
            # Registrar atividade
            self._log_user_activity(
                user_id, 
                "flow_executed", 
                f"Flow '{flow.name}' executado - Status: {execution.status}"
            )
            
            return self._build_execution_response(execution)
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.execution_time = time.time() - start_time
            execution.completed_at = datetime.utcnow()
            
            self.db.commit()
            
            return self._build_execution_response(execution)
    
    def get_flow_executions(self, flow_id: int, user_id: int, limit: int = 50) -> List[FlowExecutionResponse]:
        """
        Busca execuções do flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            limit: Limite de execuções
            
        Returns:
            Lista de execuções
        """
        executions = self.db.query(FlowExecution).filter(
            and_(
                FlowExecution.flow_id == flow_id,
                FlowExecution.user_id == user_id
            )
        ).order_by(desc(FlowExecution.started_at)).limit(limit).all()
        
        return [self._build_execution_response(execution) for execution in executions]
    
    def get_flow_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca templates de flows
        
        Args:
            category: Categoria dos templates
            
        Returns:
            Lista de templates
        """
        query = self.db.query(FlowTemplate).filter(FlowTemplate.is_public == True)
        
        if category:
            query = query.filter(FlowTemplate.category == category)
        
        templates = query.order_by(desc(FlowTemplate.usage_count)).all()
        
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "usage_count": template.usage_count,
                "template_data": json.loads(template.template_data)
            }
            for template in templates
        ]
    
    async def _execute_step(self, step: FlowStep, input_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Executa uma etapa do flow
        
        Args:
            step: Etapa a ser executada
            input_data: Dados de entrada
            user_id: ID do usuário
            
        Returns:
            Resultado da execução da etapa
        """
        start_time = time.time()
        started_at = datetime.utcnow()
        
        try:
            config = json.loads(step.config) if step.config else {}
            
            if step.step_type == StepType.AGENT_EXECUTION:
                # Executar agente
                agent_id = config.get("agent_id")
                message = config.get("message", "").format(**input_data)
                
                result = await self.agent_service.execute_agent(
                    agent_id=agent_id,
                    user_id=user_id,
                    user_message=message,
                    context=input_data
                )
                
                return {
                    "success": result["success"],
                    "output": {"agent_response": result["response"]},
                    "execution_time": time.time() - start_time,
                    "started_at": started_at,
                    "error_message": result.get("error_message")
                }
            
            elif step.step_type == StepType.ORION_SERVICE:
                # Chamar serviço do Orion
                service_type = config.get("service_type")
                file_url = input_data.get("file_url") or config.get("file_url")
                
                result = await self.orion_service.call_service(
                    service_type=service_type,
                    file_url=file_url,
                    parameters=config.get("parameters", {})
                )
                
                return {
                    "success": result["status"] == "success",
                    "output": result.get("result", {}),
                    "execution_time": time.time() - start_time,
                    "started_at": started_at,
                    "error_message": result.get("error_message")
                }
            
            elif step.step_type == StepType.PAUSE_FOR_REVIEW:
                # Pausar para revisão (sempre sucesso)
                return {
                    "success": True,
                    "output": {"paused_for_review": True},
                    "execution_time": time.time() - start_time,
                    "started_at": started_at
                }
            
            elif step.step_type == StepType.CONDITION:
                # Avaliar condição
                condition = config.get("condition", "True")
                # TODO: Implementar avaliação segura de condições
                result = True  # Por enquanto, sempre verdadeiro
                
                return {
                    "success": True,
                    "output": {"condition_result": result},
                    "execution_time": time.time() - start_time,
                    "started_at": started_at
                }
            
            else:
                return {
                    "success": False,
                    "output": {},
                    "execution_time": time.time() - start_time,
                    "started_at": started_at,
                    "error_message": f"Tipo de etapa não suportado: {step.step_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "output": {},
                "execution_time": time.time() - start_time,
                "started_at": started_at,
                "error_message": str(e)
            }
    
    def _build_flow_response(self, flow: Flow) -> FlowResponse:
        """Constrói resposta do flow com etapas"""
        steps = self.db.query(FlowStep).filter(
            FlowStep.flow_id == flow.id
        ).order_by(FlowStep.order).all()
        
        return FlowResponse(
            id=flow.id,
            user_id=flow.user_id,
            name=flow.name,
            description=flow.description,
            status=flow.status,
            tags=json.loads(flow.tags) if flow.tags else [],
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            last_executed=flow.last_executed,
            execution_count=flow.execution_count,
            estimated_time=flow.estimated_time,
            steps=[
                {
                    "id": step.id,
                    "flow_id": step.flow_id,
                    "name": step.name,
                    "step_type": step.step_type,
                    "order": step.order,
                    "description": step.description,
                    "config": json.loads(step.config) if step.config else {},
                    "created_at": step.created_at,
                    "updated_at": step.updated_at
                }
                for step in steps
            ]
        )
    
    def _build_execution_response(self, execution: FlowExecution) -> FlowExecutionResponse:
        """Constrói resposta da execução"""
        flow = self.db.query(Flow).filter(Flow.id == execution.flow_id).first()
        
        # Buscar resultados das etapas
        step_results = self.db.query(FlowExecutionStep).filter(
            FlowExecutionStep.execution_id == execution.id
        ).all()
        
        return FlowExecutionResponse(
            id=execution.id,
            flow_id=execution.flow_id,
            flow_name=flow.name if flow else "Unknown",
            user_id=execution.user_id,
            status=execution.status,
            input_data=json.loads(execution.input_data) if execution.input_data else {},
            output_data=json.loads(execution.output_data) if execution.output_data else None,
            current_step=execution.current_step,
            total_steps=execution.total_steps,
            completed_steps=execution.completed_steps,
            error_message=execution.error_message,
            execution_time=execution.execution_time,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            steps_results=[
                {
                    "step_id": step.step_id,
                    "step_name": "Unknown",  # TODO: Buscar nome da etapa
                    "status": step.status,
                    "input_data": json.loads(step.input_data) if step.input_data else None,
                    "output_data": json.loads(step.output_data) if step.output_data else None,
                    "error_message": step.error_message,
                    "execution_time": step.execution_time,
                    "started_at": step.started_at,
                    "completed_at": step.completed_at
                }
                for step in step_results
            ]
        )
    
    def _calculate_estimated_time(self, steps: List) -> int:
        """Calcula tempo estimado do flow em segundos"""
        # Estimativa básica: 30 segundos por etapa
        return len(steps) * 30
    
    def _log_user_activity(self, user_id: int, activity_type: str, description: str):
        """Registra atividade do usuário"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description
        )
        
        self.db.add(activity)
        # Não fazer commit aqui, deixar para o método principal

