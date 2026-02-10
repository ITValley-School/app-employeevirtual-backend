"""
Repositório de agentes de sistema para o sistema EmployeeVirtual
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from data.entities.system_agent_entities import SystemAgentEntity


class SystemAgentRepository:
    """Repositório para operações de dados de agentes de sistema"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, agent_id: str) -> Optional[SystemAgentEntity]:
        """Busca agente de sistema por ID (apenas ativos)"""
        return self.db.query(SystemAgentEntity).filter(
            and_(
                SystemAgentEntity.id == agent_id,
                SystemAgentEntity.is_active == True
            )
        ).first()
    
    def list_all(self) -> List[SystemAgentEntity]:
        """Lista todos os agentes de sistema ativos"""
        return self.db.query(SystemAgentEntity).filter(
            SystemAgentEntity.is_active == True
        ).all()
    
    def get_by_type(self, agent_type: str) -> List[SystemAgentEntity]:
        """Lista agentes de sistema por tipo"""
        return self.db.query(SystemAgentEntity).filter(
            and_(
                SystemAgentEntity.agent_type == agent_type,
                SystemAgentEntity.is_active == True
            )
        ).all()
    
    def create_system_agent(self, agent: SystemAgentEntity) -> SystemAgentEntity:
        """Cria novo agente de sistema"""
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def update_system_agent(self, agent: SystemAgentEntity) -> SystemAgentEntity:
        """Atualiza agente de sistema"""
        self.db.merge(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

