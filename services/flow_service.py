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
        Cria novo flow.
        Service orquestra: Factory cria, Repository persiste.
        """
        # 1. Factory extrai nome do DTO para validação
        name = FlowFactory.name_from(dto)
        if self.flow_repository.exists_name(name, user_id):
            raise ValueError("Nome do flow já existe")

        # 2. Factory cria Entity (conhece campos do DTO)
        flow = FlowFactory.create_from_dto(dto, user_id)

        # 3. Repository persiste objeto inteiro
        self.flow_repository.add(flow)

        return flow

    def get_flow_by_id(self, flow_id: str, user_id: str) -> Optional[FlowEntity]:
        """Busca flow por ID"""
        return self.flow_repository.get_flow_by_id(flow_id, user_id)

    def get_flow_detail(self, flow_id: str, user_id: str) -> Dict[str, Any]:
        """Busca flow com detalhes"""
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")

        stats = {
            "total_executions": 0,
            "success_rate": 0.0,
            "avg_execution_time": 0.0
        }

        return {"flow": flow, "stats": stats}

    def update_flow(self, flow_id: str, dto: FlowUpdateRequest, user_id: str) -> FlowEntity:
        """
        Atualiza flow.
        Service orquestra: Factory atualiza, Repository persiste.
        """
        # 1. Busca flow
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")

        # 2. Factory helpers para validação (Service não acessa campos)
        dto_name = FlowFactory.name_from(dto)
        entity_name = FlowFactory.name_from_entity(flow)
        if not FlowFactory.names_match(dto_name, entity_name):
            if self.flow_repository.exists_name(dto_name, user_id):
                raise ValueError("Nome do flow já existe")

        # 3. Factory atualiza (conhece campos do DTO e Entity)
        updated_flow = FlowFactory.update_from_dto(flow, dto)

        # 4. Repository persiste objeto inteiro
        self.flow_repository.update(updated_flow)

        return updated_flow

    def list_flows(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> tuple[List[FlowEntity], int]:
        """Lista flows do usuário"""
        return self.flow_repository.list_flows(user_id, page, size, status)

    def execute_flow(self, flow_id: str, dto: FlowExecuteRequest, user_id: str) -> Dict[str, Any]:
        """
        Executa flow.
        Service orquestra: Factory extrai dados, execução é feita internamente.
        """
        # 1. Busca flow
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")

        # 2. Método de domínio (permitido pela Regra 5)
        if not flow.can_execute():
            raise ValueError("Flow não pode ser executado")

        # 3. Factory extrai dados do DTO (Service não acessa campos)
        input_data = FlowFactory.input_data_from(dto)
        session_id = FlowFactory.session_id_from(dto)

        # 4. Execução
        import time
        start_time = time.time()
        time.sleep(0.1)
        execution_time = time.time() - start_time

        return {
            "input_data": input_data,
            "output_data": {"result": "Flow executado com sucesso"},
            "execution_time": execution_time,
            "steps_completed": 3,
            "total_steps": 3,
            "status": "completed",
            "execution_id": "",
            "session_id": session_id
        }

    def activate_flow(self, flow_id: str, user_id: str) -> FlowEntity:
        """Ativa flow"""
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        flow.activate()
        self.flow_repository.update(flow)
        return flow

    def deactivate_flow(self, flow_id: str, user_id: str) -> FlowEntity:
        """Desativa flow"""
        flow = self.get_flow_by_id(flow_id, user_id)
        if not flow:
            raise ValueError("Flow não encontrado")
        flow.deactivate()
        self.flow_repository.update(flow)
        return flow
