"""
Repositório de agentes para o sistema EmployeeVirtual
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from data.entities.agent_entities import AgentEntity


class AgentRepository:
    """Repositório para operações de dados de agentes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_agent_by_id(self, agent_id: str, user_id: str) -> Optional[AgentEntity]:
        """Busca agente por ID, verificando se pertence ao usuário"""
        return self.db.query(AgentEntity).filter(
            and_(
                AgentEntity.id == agent_id,
                AgentEntity.user_id == user_id
            )
        ).first()
    
    def list_agents_by_user(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> Tuple[List[AgentEntity], int]:
        """Lista agentes do usuário com paginação"""
        query = self.db.query(AgentEntity).filter(AgentEntity.user_id == user_id)
        
        # Filtro por status: usa "active" como padrão se não fornecido
        if status:
            query = query.filter(AgentEntity.status == status)
        else:
            # Retorna apenas agentes ativos por padrão
            query = query.filter(AgentEntity.status == "active")
        
        # Total de registros
        total = query.count()
        
        # Paginação - MSSQL requer ORDER BY com OFFSET
        skip = (page - 1) * size
        agents = query.order_by(desc(AgentEntity.created_at)).offset(skip).limit(size).all()
        
        return agents, total
    
    def create_agent(self, agent: AgentEntity) -> AgentEntity:
        """Cria novo agente"""
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def update_agent(self, agent: AgentEntity) -> AgentEntity:
        """Atualiza agente"""
        self.db.merge(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """Deleta agente se pertencer ao usuário"""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            return False
        
        self.db.delete(agent)
        self.db.commit()
        return True
