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
        """
        Cria FlowEntity a partir de DTO
        
        Args:
            dto: Dados do flow
            user_id: ID do usuário
            
        Returns:
            FlowEntity: Flow criado
        """
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
        """
        Atualiza FlowEntity a partir de DTO
        
        Args:
            flow: Flow existente
            dto: Dados para atualização
            
        Returns:
            FlowEntity: Flow atualizado
        """
        if dto.name is not None:
            flow.name = dto.name
        if dto.description is not None:
            flow.description = dto.description
        if dto.steps is not None:
            flow.steps = dto.steps
        
        flow.updated_at = datetime.utcnow()
        return flow
