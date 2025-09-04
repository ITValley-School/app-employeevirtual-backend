"""
Repository para acesso a dados de agentes - Camada Data
"""
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime

from models.agent_models import (
    Agent, AgentKnowledge, AgentExecutionDB, SystemAgent,
    AgentCreate, AgentUpdate, AgentResponse
)
from models.user_models import UserActivity


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
    
    def create_agent(self, agent_data: Dict[str, Any]) -> Agent:
        """
        Cria um novo agente no banco
        
        Args:
            agent_data: Dados do agente já validados
            
        Returns:
            Agent: Instância do agente criado
        """
        # Gerar UUID para o agente
        agent_data["id"] = str(uuid.uuid4())
        
        db_agent = Agent(**agent_data)
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        return db_agent
    
    def get_agent_by_id(self, agent_id: str, user_id: Optional[str] = None) -> Optional[Agent]:
        """
        Busca agente por ID
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário (filtro opcional)
            
        Returns:
            Agent ou None
        """
        query = self.db.query(Agent).filter(Agent.id == agent_id)
        
        if user_id:
            query = query.filter(Agent.user_id == user_id)
        
        return query.first()
    
    def get_agents_by_user(self, user_id: str, include_system: bool = True) -> List[Agent]:
        """
        Busca agentes do usuário
        
        Args:
            user_id: ID do usuário
            include_system: Incluir agentes do sistema
            
        Returns:
            Lista de agentes
        """
        query = self.db.query(Agent).filter(Agent.user_id == user_id)
        
        if not include_system:
            query = query.filter(Agent.agent_type == "custom")
        
        return query.order_by(desc(Agent.created_at)).all()
    
    def update_agent(self, agent_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Agent]:
        """
        Atualiza agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            update_data: Dados para atualização
            
        Returns:
            Agent atualizado ou None
        """
        agent = self.db.query(Agent).filter(
            and_(Agent.id == agent_id, Agent.user_id == user_id)
        ).first()
        
        if not agent:
            return None
        
        # Aplicar atualizações
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(agent)
        
        return agent
    
    def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """
        Deleta agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            True se deletado com sucesso
        """
        agent = self.db.query(Agent).filter(
            and_(Agent.id == agent_id, Agent.user_id == user_id)
        ).first()
        
        if not agent:
            return False
        
        self.db.delete(agent)
        self.db.commit()
        return True
    
    def update_agent_stats(self, agent_id: str, usage_increment: int = 1) -> None:
        """
        Atualiza estatísticas do agente
        
        Args:
            agent_id: ID do agente
            usage_increment: Incremento no contador de uso
        """
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            agent.last_used = datetime.utcnow()
            agent.usage_count += usage_increment
            self.db.commit()
    
    # ==========================================
    # OPERAÇÕES - EXECUÇÕES
    # ==========================================
    
    def create_execution(self, execution_data: Dict[str, Any]) -> AgentExecutionDB:
        """
        Cria registro de execução
        
        Args:
            execution_data: Dados da execução
            
        Returns:
            AgentExecutionDB: Execução criada
        """
        # Gerar UUID para a execução se não fornecido
        if "id" not in execution_data:
            execution_data["id"] = str(uuid.uuid4())
            
        execution = AgentExecutionDB(**execution_data)
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def get_agent_executions(self, agent_id: str, user_id: str, limit: int = 50) -> List[AgentExecutionDB]:
        """
        Busca execuções do agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            limit: Limite de registros
            
        Returns:
            Lista de execuções
        """
        return self.db.query(AgentExecutionDB).filter(
            and_(
                AgentExecutionDB.agent_id == agent_id,
                AgentExecutionDB.user_id == user_id
            )
        ).order_by(desc(AgentExecutionDB.created_at)).limit(limit).all()
    
    # ==========================================
    # OPERAÇÕES - BASE DE CONHECIMENTO
    # ==========================================
    
    def create_knowledge(self, knowledge_data: Dict[str, Any]) -> AgentKnowledge:
        """
        Adiciona conhecimento ao agente
        
        Args:
            knowledge_data: Dados do conhecimento
            
        Returns:
            AgentKnowledge: Conhecimento criado
        """
        # Gerar UUID para o conhecimento se não fornecido
        if "id" not in knowledge_data:
            knowledge_data["id"] = str(uuid.uuid4())
            
        knowledge = AgentKnowledge(**knowledge_data)
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge
    
    def get_agent_knowledge(self, agent_id: str) -> List[AgentKnowledge]:
        """
        Busca conhecimento do agente
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Lista de arquivos de conhecimento
        """
        return self.db.query(AgentKnowledge).filter(
            AgentKnowledge.agent_id == agent_id
        ).all()
    
    # ==========================================
    # OPERAÇÕES - AGENTES DO SISTEMA
    # ==========================================
    
    def get_system_agents(self) -> List[SystemAgent]:
        """
        Busca agentes do sistema
        
        Returns:
            Lista de agentes do sistema
        """
        return self.db.query(SystemAgent).filter(
            SystemAgent.is_active == True
        ).all()
    
    # ==========================================
    # OPERAÇÕES - ATIVIDADES
    # ==========================================
    
    def log_user_activity(self, activity_data: Dict[str, Any]) -> UserActivity:
        """
        Registra atividade do usuário
        
        Args:
            activity_data: Dados da atividade
            
        Returns:
            UserActivity: Atividade criada
        """
        activity = UserActivity(**activity_data)
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
