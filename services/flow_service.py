"""
Serviço de flows/automações para o sistema EmployeeVirtual - Nova implementação
Usa apenas repositories para acesso a dados
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from data.flow_repository import FlowRepository
from data.agent_repository import AgentRepository
from data.user_repository import UserRepository
from models.flow_models import (
    FlowCreate, FlowUpdate, FlowResponse, FlowWithSteps,
    FlowStepCreate, FlowStepUpdate, FlowStepResponse,
    FlowExecutionCreate, FlowExecutionResponse,
    FlowStatus, ExecutionStatus, StepType
)


class FlowService:
    """Serviço para gerenciamento de flows/automações - Nova implementação"""
    
    def __init__(self, db: Session):
        self.flow_repository = FlowRepository(db)
        self.agent_repository = AgentRepository(db)
        self.user_repository = UserRepository(db)
    
    def create_flow(self, user_id: int, flow_data: FlowCreate) -> FlowResponse:
        """
        Cria um novo flow
        
        Args:
            user_id: ID do usuário
            flow_data: Dados do flow
            
        Returns:
            FlowResponse: Dados do flow criado
        """
        # Verificar se já existe flow com esse nome
        existing_flow = self.flow_repository.get_flow_by_name(user_id, flow_data.name)
        if existing_flow:
            raise ValueError("Já existe um flow com esse nome")
        
        # Criar flow
        flow = self.flow_repository.create_flow(
            user_id=user_id,
            name=flow_data.name,
            description=flow_data.description,
            config=flow_data.config
        )
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="flow_created",
            description=f"Flow '{flow_data.name}' criado"
        )
        
        return FlowResponse(
            id=flow.id,
            user_id=flow.user_id,
            name=flow.name,
            description=flow.description,
            status=flow.status,
            config=flow.config,
            step_count=0,
            created_at=flow.created_at,
            updated_at=flow.updated_at
        )
    
    def get_flow_by_id(self, flow_id: int, user_id: int) -> Optional[FlowResponse]:
        """
        Busca flow por ID
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            FlowResponse ou None se não encontrado
        """
        flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
        if not flow:
            return None
        
        # Contar etapas
        steps = self.flow_repository.get_flow_steps(flow_id)
        
        return FlowResponse(
            id=flow.id,
            user_id=flow.user_id,
            name=flow.name,
            description=flow.description,
            status=flow.status,
            config=flow.config,
            step_count=len(steps),
            created_at=flow.created_at,
            updated_at=flow.updated_at
        )
    
    def get_flow_with_steps(self, flow_id: int, user_id: int) -> Optional[FlowWithSteps]:
        """
        Busca flow com suas etapas
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            FlowWithSteps ou None se não encontrado
        """
        flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
        if not flow:
            return None
        
        # Buscar etapas
        steps = self.flow_repository.get_flow_steps(flow_id)
        
        # Converter etapas
        step_responses = []
        for step in steps:
            step_responses.append(FlowStepResponse(
                id=step.id,
                flow_id=step.flow_id,
                name=step.name,
                step_type=step.step_type,
                order=step.order,
                description=step.description,
                config=step.config,
                created_at=step.created_at,
                updated_at=step.updated_at
            ))
        
        return FlowWithSteps(
            id=flow.id,
            user_id=flow.user_id,
            name=flow.name,
            description=flow.description,
            status=flow.status,
            config=flow.config,
            steps=step_responses,
            created_at=flow.created_at,
            updated_at=flow.updated_at
        )
    
    def get_user_flows(self, user_id: int, status: FlowStatus = None, 
                      skip: int = 0, limit: int = 50) -> List[FlowResponse]:
        """
        Busca flows do usuário
        
        Args:
            user_id: ID do usuário
            status: Status específico (opcional)
            skip: Offset para paginação
            limit: Limite de resultados
            
        Returns:
            Lista de flows
        """
        flows = self.flow_repository.get_user_flows(user_id, skip, limit, status)
        
        result = []
        for flow in flows:
            # Contar etapas
            steps = self.flow_repository.get_flow_steps(flow.id)
            
            result.append(FlowResponse(
                id=flow.id,
                user_id=flow.user_id,
                name=flow.name,
                description=flow.description,
                status=flow.status,
                config=flow.config,
                step_count=len(steps),
                created_at=flow.created_at,
                updated_at=flow.updated_at
            ))
        
        return result
    
    def update_flow(self, flow_id: int, user_id: int, flow_data: FlowUpdate) -> Optional[FlowResponse]:
        """
        Atualiza dados do flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            flow_data: Dados para atualização
            
        Returns:
            FlowResponse ou None se não encontrado
        """
        # Verificar se nome já está em uso por outro flow
        if flow_data.name:
            existing_flow = self.flow_repository.get_flow_by_name(user_id, flow_data.name)
            if existing_flow and existing_flow.id != flow_id:
                raise ValueError("Já existe outro flow com esse nome")
        
        # Preparar dados para atualização
        update_data = {}
        if flow_data.name is not None:
            update_data['name'] = flow_data.name
        if flow_data.description is not None:
            update_data['description'] = flow_data.description
        if flow_data.status is not None:
            update_data['status'] = flow_data.status
        if flow_data.config is not None:
            update_data['config'] = flow_data.config
        
        # Atualizar flow
        flow = self.flow_repository.update_flow(flow_id, user_id, **update_data)
        if not flow:
            return None
        
        # Contar etapas
        steps = self.flow_repository.get_flow_steps(flow_id)
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="flow_updated",
            description=f"Flow '{flow.name}' atualizado"
        )
        
        return FlowResponse(
            id=flow.id,
            user_id=flow.user_id,
            name=flow.name,
            description=flow.description,
            status=flow.status,
            config=flow.config,
            step_count=len(steps),
            created_at=flow.created_at,
            updated_at=flow.updated_at
        )
    
    def delete_flow(self, flow_id: int, user_id: int) -> bool:
        """
        Remove um flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            True se removido com sucesso
        """
        # Buscar nome do flow para log
        flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
        if not flow:
            return False
        
        flow_name = flow.name
        
        # Remover flow
        success = self.flow_repository.delete_flow(flow_id, user_id)
        
        if success:
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="flow_deleted",
                description=f"Flow '{flow_name}' removido"
            )
        
        return success
    
    def activate_flow(self, flow_id: int, user_id: int) -> bool:
        """
        Ativa um flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            True se ativado com sucesso
        """
        success = self.flow_repository.activate_flow(flow_id, user_id)
        
        if success:
            # Registrar atividade
            flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="flow_activated",
                description=f"Flow '{flow.name}' ativado"
            )
        
        return success
    
    def deactivate_flow(self, flow_id: int, user_id: int) -> bool:
        """
        Desativa um flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            True se desativado com sucesso
        """
        success = self.flow_repository.deactivate_flow(flow_id, user_id)
        
        if success:
            # Registrar atividade
            flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="flow_deactivated",
                description=f"Flow '{flow.name}' desativado"
            )
        
        return success
    
    def pause_flow(self, flow_id: int, user_id: int) -> bool:
        """
        Pausa um flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            True se pausado com sucesso
        """
        success = self.flow_repository.pause_flow(flow_id, user_id)
        
        if success:
            # Registrar atividade
            flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="flow_paused",
                description=f"Flow '{flow.name}' pausado"
            )
        
        return success
    
    # Métodos para etapas de flow
    def add_flow_step(self, flow_id: int, user_id: int, step_data: FlowStepCreate) -> FlowStepResponse:
        """
        Adiciona uma etapa ao flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            step_data: Dados da etapa
            
        Returns:
            FlowStepResponse: Etapa criada
        """
        # Verificar se flow existe e pertence ao usuário
        flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        # Validar configurações específicas por tipo de etapa
        if step_data.step_type == StepType.AGENT_EXECUTION:
            agent_id = step_data.config.get('agent_id')
            if not agent_id:
                raise ValueError("agent_id é obrigatório para etapas de execução de agente")
            
            # Verificar se agente existe e pertence ao usuário
            agent = self.agent_repository.get_agent_by_id(agent_id, user_id)
            if not agent:
                raise ValueError("Agente não encontrado")
        
        # Criar etapa
        step = self.flow_repository.create_flow_step(
            flow_id=flow_id,
            name=step_data.name,
            step_type=step_data.step_type,
            order=step_data.order,
            description=step_data.description,
            config=step_data.config
        )
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="flow_step_added",
            description=f"Etapa '{step_data.name}' adicionada ao flow '{flow.name}'"
        )
        
        return FlowStepResponse(
            id=step.id,
            flow_id=step.flow_id,
            name=step.name,
            step_type=step.step_type,
            order=step.order,
            description=step.description,
            config=step.config,
            created_at=step.created_at,
            updated_at=step.updated_at
        )
    
    def update_flow_step(self, step_id: int, user_id: int, step_data: FlowStepUpdate) -> Optional[FlowStepResponse]:
        """
        Atualiza uma etapa do flow
        
        Args:
            step_id: ID da etapa
            user_id: ID do usuário
            step_data: Dados para atualização
            
        Returns:
            FlowStepResponse ou None se não encontrada
        """
        # Buscar etapa e verificar permissão
        step = self.flow_repository.get_flow_step_by_id(step_id)
        if not step:
            return None
        
        flow = self.flow_repository.get_flow_by_id(step.flow_id, user_id)
        if not flow:
            return None
        
        # Preparar dados para atualização
        update_data = {}
        if step_data.name is not None:
            update_data['name'] = step_data.name
        if step_data.description is not None:
            update_data['description'] = step_data.description
        if step_data.order is not None:
            update_data['order'] = step_data.order
        if step_data.config is not None:
            update_data['config'] = step_data.config
        
        # Atualizar etapa
        updated_step = self.flow_repository.update_flow_step(step_id, **update_data)
        if not updated_step:
            return None
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="flow_step_updated",
            description=f"Etapa '{updated_step.name}' atualizada"
        )
        
        return FlowStepResponse(
            id=updated_step.id,
            flow_id=updated_step.flow_id,
            name=updated_step.name,
            step_type=updated_step.step_type,
            order=updated_step.order,
            description=updated_step.description,
            config=updated_step.config,
            created_at=updated_step.created_at,
            updated_at=updated_step.updated_at
        )
    
    def delete_flow_step(self, step_id: int, user_id: int) -> bool:
        """
        Remove uma etapa do flow
        
        Args:
            step_id: ID da etapa
            user_id: ID do usuário
            
        Returns:
            True se removida com sucesso
        """
        # Buscar etapa e verificar permissão
        step = self.flow_repository.get_flow_step_by_id(step_id)
        if not step:
            return False
        
        flow = self.flow_repository.get_flow_by_id(step.flow_id, user_id)
        if not flow:
            return False
        
        step_name = step.name
        
        # Remover etapa
        success = self.flow_repository.delete_flow_step(step_id)
        
        if success:
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="flow_step_deleted",
                description=f"Etapa '{step_name}' removida"
            )
        
        return success
    
    def reorder_flow_steps(self, flow_id: int, user_id: int, step_orders: List[Dict[str, int]]) -> bool:
        """
        Reordena etapas do flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            step_orders: Lista com novos ordenamentos
            
        Returns:
            True se reordenado com sucesso
        """
        # Verificar permissão
        flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
        if not flow:
            return False
        
        # Reordenar etapas
        success = self.flow_repository.reorder_flow_steps(flow_id, step_orders)
        
        if success:
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="flow_steps_reordered",
                description=f"Etapas do flow '{flow.name}' reordenadas"
            )
        
        return success
    
    # Métodos para execuções
    def execute_flow(self, flow_id: int, user_id: int, trigger_data: Dict[str, Any] = None) -> FlowExecutionResponse:
        """
        Executa um flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            trigger_data: Dados de entrada
            
        Returns:
            FlowExecutionResponse: Execução criada
        """
        # Verificar se flow existe, pertence ao usuário e está ativo
        flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        if flow.status != FlowStatus.ACTIVE:
            raise ValueError("Flow não está ativo")
        
        # Verificar se flow tem etapas
        steps = self.flow_repository.get_flow_steps(flow_id)
        if not steps:
            raise ValueError("Flow não possui etapas configuradas")
        
        # Criar execução
        execution = self.flow_repository.create_flow_execution(
            flow_id=flow_id,
            user_id=user_id,
            trigger_data=trigger_data or {}
        )
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="flow_executed",
            description=f"Flow '{flow.name}' executado"
        )
        
        return FlowExecutionResponse(
            id=execution.id,
            flow_id=execution.flow_id,
            flow_name=flow.name,
            user_id=execution.user_id,
            status=execution.status,
            trigger_data=execution.trigger_data,
            result=execution.result,
            error_message=execution.error_message,
            duration=execution.duration,
            time_saved=execution.time_saved,
            created_at=execution.created_at,
            started_at=execution.started_at,
            ended_at=execution.ended_at
        )
    
    def get_flow_executions(self, flow_id: int = None, user_id: int = None, 
                           status: ExecutionStatus = None, skip: int = 0, 
                           limit: int = 50) -> List[FlowExecutionResponse]:
        """
        Busca execuções de flows
        
        Args:
            flow_id: ID específico do flow (opcional)
            user_id: ID do usuário
            status: Status específico (opcional)
            skip: Offset para paginação
            limit: Limite de resultados
            
        Returns:
            Lista de execuções
        """
        executions = self.flow_repository.get_flow_executions(flow_id, user_id, skip, limit, status)
        
        result = []
        for execution in executions:
            # Buscar nome do flow
            flow = self.flow_repository.get_flow_by_id(execution.flow_id)
            flow_name = flow.name if flow else "Flow não encontrado"
            
            result.append(FlowExecutionResponse(
                id=execution.id,
                flow_id=execution.flow_id,
                flow_name=flow_name,
                user_id=execution.user_id,
                status=execution.status,
                trigger_data=execution.trigger_data,
                result=execution.result,
                error_message=execution.error_message,
                duration=execution.duration,
                time_saved=execution.time_saved,
                created_at=execution.created_at,
                started_at=execution.started_at,
                ended_at=execution.ended_at
            ))
        
        return result
    
    def get_flow_statistics(self, flow_id: int, user_id: int) -> Dict[str, Any]:
        """
        Busca estatísticas de um flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            Estatísticas do flow
        """
        # Verificar permissão
        flow = self.flow_repository.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        return self.flow_repository.get_flow_statistics(flow_id)
    
    def search_flows(self, user_id: int, query: str, status: FlowStatus = None, 
                    limit: int = 50) -> List[FlowResponse]:
        """
        Busca flows por texto
        
        Args:
            user_id: ID do usuário
            query: Texto para busca
            status: Status específico (opcional)
            limit: Limite de resultados
            
        Returns:
            Lista de flows encontrados
        """
        flows = self.flow_repository.search_flows(user_id, query, status, limit)
        
        result = []
        for flow in flows:
            # Contar etapas
            steps = self.flow_repository.get_flow_steps(flow.id)
            
            result.append(FlowResponse(
                id=flow.id,
                user_id=flow.user_id,
                name=flow.name,
                description=flow.description,
                status=flow.status,
                config=flow.config,
                step_count=len(steps),
                created_at=flow.created_at,
                updated_at=flow.updated_at
            ))
        
        return result
