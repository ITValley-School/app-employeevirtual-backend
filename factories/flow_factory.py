"""
Factory para flows
Cria objetos do domínio seguindo padrão IT Valley Architecture
"""
from typing import Optional
from datetime import datetime
from uuid import uuid4

from schemas.flows.requests import FlowCreateRequest, FlowUpdateRequest
from domain.flows.flow_entity import FlowEntity


class FlowFactory:
    """Factory para criação de flows"""

    @staticmethod
    def create_from_dto(dto: FlowCreateRequest, user_id: str) -> FlowEntity:
        """Cria FlowEntity a partir de DTO"""
        return FlowEntity(
            id=str(uuid4()),
            name=dto.name,
            description=dto.description,
            steps=dto.steps,
            user_id=user_id,
            status="draft",
            created_at=datetime.utcnow()
        )

    @staticmethod
    def update_from_dto(flow: FlowEntity, dto: FlowUpdateRequest) -> FlowEntity:
        """Atualiza FlowEntity a partir de DTO"""
        if dto.name is not None:
            flow.name = dto.name
        if dto.description is not None:
            flow.description = dto.description
        if dto.steps is not None:
            flow.steps = dto.steps
        flow.updated_at = datetime.utcnow()
        return flow

    # ========== HELPERS PARA DTO ==========

    @staticmethod
    def name_from(dto) -> Optional[str]:
        """Extrai nome do DTO"""
        if hasattr(dto, 'name'):
            return dto.name
        if isinstance(dto, dict):
            return dto.get('name')
        return None

    @staticmethod
    def input_data_from(dto) -> dict:
        """Extrai input_data do DTO de execução"""
        if hasattr(dto, 'input_data'):
            return dto.input_data or {}
        if isinstance(dto, dict):
            return dto.get('input_data', {})
        return {}

    @staticmethod
    def session_id_from(dto) -> Optional[str]:
        """Extrai session_id do DTO de execução"""
        if hasattr(dto, 'session_id'):
            return dto.session_id
        if isinstance(dto, dict):
            return dto.get('session_id')
        return None

    # ========== HELPERS PARA ENTITY ==========

    @staticmethod
    def name_from_entity(flow) -> str:
        """Extrai nome da entidade de flow"""
        return getattr(flow, 'name', '')

    @staticmethod
    def names_match(dto_name: Optional[str], entity_name: str) -> bool:
        """Verifica se o nome do DTO é igual ao nome da entidade"""
        if not dto_name:
            return True
        return dto_name == entity_name
