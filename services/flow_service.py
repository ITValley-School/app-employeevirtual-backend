"""
Service de flows - Orquestrador de casos de uso
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from schemas.flows.requests import FlowCreateRequest, FlowUpdateRequest, FlowExecuteRequest
from domain.flows.flow_entity import FlowEntity
from factories.flow_factory import FlowFactory
from data.flow_repository import FlowRepository


class FlowService:
    """Service para orquestração de flows"""
    
    def __init__(self, db: Session):
        self.db = db
        self.flow_repository = FlowRepository(db)
    
    def create_flow(self, dto: FlowCreateRequest, user_id: str) -> FlowEntity:
        """
        Cria novo flow
        
        Args:
            dto: Dados do flow
            user_id: ID do usuário
            
        Returns:
            FlowEntity: Flow criado
        """
        # 1. Validações que dependem do repositório
        if self.flow_repository.exists_name(dto.name, user_id):
            raise ValueError("Nome do flow já existe")
        
        # 2. Factory cria Entity a partir do DTO
        flow = FlowFactory.create_from_dto(dto, user_id)
        
        # 3. Repository persiste Entity
        self.flow_repository.add(flow)
        
        return flow
    
    def get_flow_by_id(self, flow_id: str, user_id: str) -> Optional[FlowEntity]:
        """
        Busca flow por ID
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            FlowEntity: Flow encontrado ou None
        """
        return self.flow_repository.get_flow_by_id(flow_id, user_id)
    
    def get_flow_detail(self, flow_id: str, user_id: str) -> Dict[str, Any]:
        """
        Busca flow com detalhes
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            dict: Flow e estatísticas
        """
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        # Simula estatísticas
        stats = {
            "total_executions": 0,
            "success_rate": 0.0,
            "avg_execution_time": 0.0
        }
        
        return {
            "flow": flow,
            "stats": stats
        }
    
    def update_flow(self, flow_id: str, dto: FlowUpdateRequest, user_id: str) -> FlowEntity:
        """
        Atualiza flow
        
        Args:
            flow_id: ID do flow
            dto: Dados para atualização
            user_id: ID do usuário
            
        Returns:
            FlowEntity: Flow atualizado
        """
        # 1. Busca flow
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        # 2. Validações
        if dto.name and dto.name != flow.name:
            if self.flow_repository.exists_name(dto.name, user_id):
                raise ValueError("Nome do flow já existe")
        
        # 3. Atualiza via Factory
        updated_flow = FlowFactory.update_from_dto(flow, dto)
        
        # 4. Persiste
        self.flow_repository.update(updated_flow)
        
        return updated_flow
    
    def list_flows(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> tuple[List[FlowEntity], int]:
        """
        Lista flows do usuário
        
        Args:
            user_id: ID do usuário
            page: Página
            size: Tamanho da página
            status: Filtro por status
            
        Returns:
            tuple: Lista de flows e total
        """
        return self.flow_repository.list_flows(user_id, page, size, status)
    
    def execute_flow(self, flow_id: str, dto: FlowExecuteRequest, user_id: str) -> Dict[str, Any]:
        """
        Executa flow
        
        Args:
            flow_id: ID do flow
            dto: Dados de execução
            user_id: ID do usuário
            
        Returns:
            dict: Resultado da execução
        """
        # 1. Busca flow
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        # 2. Valida se pode executar
        if not flow.can_execute():
            raise ValueError("Flow não pode ser executado")
        
        # 3. Simula execução
        import time
        start_time = time.time()
        
        # Simula processamento
        time.sleep(0.1)  # Simula processamento
        
        execution_time = time.time() - start_time
        
        return {
            "input_data": dto.input_data,
            "output_data": {"result": "Flow executado com sucesso"},
            "execution_time": execution_time,
            "steps_completed": 3,
            "session_id": dto.session_id
        }
    
    def activate_flow(self, flow_id: str, user_id: str) -> FlowEntity:
        """
        Ativa flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            FlowEntity: Flow ativado
        """
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        flow.activate()
        self.flow_repository.update(flow)
        
        return flow
    
    def deactivate_flow(self, flow_id: str, user_id: str) -> FlowEntity:
        """
        Desativa flow
        
        Args:
            flow_id: ID do flow
            user_id: ID do usuário
            
        Returns:
            FlowEntity: Flow desativado
        """
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        
        flow.deactivate()
        self.flow_repository.update(flow)
        
        return flow
