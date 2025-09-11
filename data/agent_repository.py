"""
Repository para acesso a dados de agentes - Camada Data
"""
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime

from data.entities.agent_entities import (
    AgentEntity, AgentKnowledgeEntity, AgentExecutionEntity
)
from data.entities.user_entities import UserActivityEntity
from models.agent_models import (
    AgentCreate, AgentUpdate, AgentResponse
)


class AgentRepository:
    """
    Repository para operações de banco de dados relacionadas a agentes
    Responsável apenas por acesso a dados - SEM lógica de negócio
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================
    # OPERAÇÕES CRUD - AGENTES
    # ==========================================
    
    def create_agent(self, agent_data: Dict[str, Any]) -> AgentEntity:
        """
        Cria um novo agente no banco
        
        Args:
            agent_data: Dados do agente já validados
            
        Returns:
            AgentEntity: Instância do agente criado
        """
        # Gerar UUID para o agente
        agent_data["id"] = str(uuid.uuid4())
        
        db_agent = AgentEntity(**agent_data)
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        return db_agent
    
    def get_agent_by_id(self, agent_id: str, user_id: Optional[str] = None) -> Optional[AgentEntity]:
        """
        Busca agente por ID
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário (filtro opcional)
            
        Returns:
            AgentEntity ou None
        """
        query = self.db.query(AgentEntity).filter(AgentEntity.id == agent_id)
        
        if user_id:
            query = query.filter(AgentEntity.user_id == user_id)
        
        return query.first()
    
    def get_agents_by_user(self, user_id: str, include_system: bool = True) -> List[AgentEntity]:
        """
        Busca agentes do usuário
        
        Args:
            user_id: ID do usuário
            include_system: Incluir agentes do sistema
            
        Returns:
            Lista de agentes
        """
        query = self.db.query(AgentEntity).filter(AgentEntity.user_id == user_id)
        
        if not include_system:
            query = query.filter(AgentEntity.agent_type == "custom")
        
        return query.order_by(desc(AgentEntity.created_at)).all()
    
    def update_agent(self, agent_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[AgentEntity]:
        """
        Atualiza agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            update_data: Dados para atualização
            
        Returns:
            AgentEntity atualizado ou None
        """
        AgentEntity = self.db.query(AgentEntity).filter(
            and_(AgentEntity.id == agent_id, AgentEntity.user_id == user_id)
        ).first()
        
        if not AgentEntity:
            return None
        
        # Aplicar atualizações
        for field, value in update_data.items():
            setattr(AgentEntity, field, value)
        
        AgentEntity.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(AgentEntity)
        
        return AgentEntity
    
    def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """
        Deleta agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            True se deletado com sucesso
        """
        AgentEntity = self.db.query(AgentEntity).filter(
            and_(AgentEntity.id == agent_id, AgentEntity.user_id == user_id)
        ).first()
        
        if not AgentEntity:
            return False
        
        self.db.delete(AgentEntity)
        self.db.commit()
        return True
    
    def update_agent_stats(self, agent_id: str, usage_increment: int = 1) -> None:
        """
        Atualiza estatísticas do agente
        
        Args:
            agent_id: ID do agente
            usage_increment: Incremento no contador de uso
        """
        AgentEntity = self.db.query(AgentEntity).filter(AgentEntity.id == agent_id).first()
        if AgentEntity:
            AgentEntity.last_used = datetime.utcnow()
            AgentEntity.usage_count += usage_increment
            self.db.commit()
    
    # ==========================================
    # OPERAÇÕES - EXECUÇÕES
    # ==========================================
    
    def create_execution(self, execution_data: Dict[str, Any]) -> AgentExecutionEntity:
        """
        Cria registro de execução
        
        Args:
            execution_data: Dados da execução
            
        Returns:
            AgentExecutionEntity: Execução criada
        """
        # Gerar UUID para a execução se não fornecido
        if "id" not in execution_data:
            execution_data["id"] = str(uuid.uuid4())
            
        execution = AgentExecutionEntity(**execution_data)
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def get_agent_executions(self, agent_id: str, user_id: str, limit: int = 50) -> List[AgentExecutionEntity]:
        """
        Busca execuções do agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            limit: Limite de registros
            
        Returns:
            Lista de execuções
        """
        return self.db.query(AgentExecutionEntity).filter(
            and_(
                AgentExecutionEntity.agent_id == agent_id,
                AgentExecutionEntity.user_id == user_id
            )
        ).order_by(desc(AgentExecutionEntity.created_at)).limit(limit).all()
    
    # ==========================================
    # OPERAÇÕES - BASE DE CONHECIMENTO
    # ==========================================
    
    def create_knowledge(self, knowledge_data: Dict[str, Any]) -> AgentKnowledgeEntity:
        """
        Adiciona conhecimento ao agente
        
        Args:
            knowledge_data: Dados do conhecimento
            
        Returns:
            AgentKnowledgeEntity: Conhecimento criado
        """
        # Gerar UUID para o conhecimento se não fornecido
        if "id" not in knowledge_data:
            knowledge_data["id"] = str(uuid.uuid4())
            
        knowledge = AgentKnowledgeEntity(**knowledge_data)
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge
    
    def get_agent_knowledge(self, agent_id: str) -> List[AgentKnowledgeEntity]:
        """
        Busca conhecimento do agente
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Lista de arquivos de conhecimento
        """
        return self.db.query(AgentKnowledgeEntity).filter(
            AgentKnowledgeEntity.agent_id == agent_id
        ).all()
    
    # ==========================================
    # OPERAÇÕES - ATIVIDADES
    # ==========================================
    
    def log_user_activity(self, activity_data: Dict[str, Any]) -> UserActivityEntity:
        """
        Registra atividade do usuário
        
        Args:
            activity_data: Dados da atividade
            
        Returns:
            UserActivityEntity: Atividade criada
        """
        activity = UserActivityEntity(**activity_data)
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
