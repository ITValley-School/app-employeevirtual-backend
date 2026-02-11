"""
Repositório de agentes para o sistema EmployeeVirtual
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from data.entities.agent_entities import AgentEntity
from domain.agents.agent_entity import AgentEntity as DomainAgentEntity


class AgentRepository:
    """Repositório para operações de dados de agentes"""

    def __init__(self, db: Session):
        self.db = db

    def _to_model(self, domain: DomainAgentEntity) -> AgentEntity:
        """
        Converte Domain Entity → DB Model (SQLAlchemy)
        Fronteira entre domínio e persistência.
        """
        return AgentEntity(
            id=domain.id,
            user_id=domain.user_id,
            name=domain.name,
            description=domain.description,
            agent_type=domain.type,
            system_prompt=domain.system_prompt or domain.instructions,
            personality=None,
            avatar_url=None,
            status=domain.status,
            llm_provider="openai",
            model=domain.model,
            temperature=str(domain.temperature),
            max_tokens=str(domain.max_tokens),
            created_at=domain.created_at,
            updated_at=domain.updated_at or domain.created_at,
            last_used=None,
            usage_count="0"
        )

    def _to_entity(self, model: AgentEntity) -> AgentEntity:
        """
        Retorna o DB Model diretamente.
        Como o projeto usa o DB Model (AgentEntity) como objeto de transporte,
        este método existe para manter o contrato arquitetural.
        """
        return model

    def save(self, domain: DomainAgentEntity) -> AgentEntity:
        """
        Persiste domain entity convertendo internamente.
        Service passa o objeto inteiro, Repository converte via _to_model.
        """
        model = self._to_model(domain)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

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
        """Cria novo agente (legado - prefira save())"""
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
