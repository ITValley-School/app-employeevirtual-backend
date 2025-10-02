"""
Serviço de agentes - Implementação IT Valley
Orquestra casos de uso sem implementar regras de negócio
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from schemas.agents.requests import AgentCreateRequest, AgentUpdateRequest, AgentExecuteRequest
from schemas.agents.responses import AgentResponse, AgentDetailResponse, AgentListResponse
from domain.agents.agent_entity import AgentEntity
from factories.agent_factory import AgentFactory
from mappers.agent_mapper import AgentMapper


class AgentService:
    """
    Serviço de agentes - Orquestrador
    Coordena fluxos sem implementar regras de negócio
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_agent(self, dto: AgentCreateRequest, user_id: str) -> AgentEntity:
        """
        Cria novo agente
        
        Args:
            dto: Dados para criação
            user_id: ID do usuário
            
        Returns:
            AgentEntity: Agente criado
            
        Raises:
            ValueError: Se dados inválidos
        """
        # 1. Validações básicas
        name = AgentFactory.name_from(dto)
        if not name:
            raise ValueError("Nome do agente é obrigatório")
        
        # 2. Cria entidade via Factory
        dto.user_id = user_id
        agent = AgentFactory.create_agent(dto)
        
        # 3. Simula persistência (em implementação real, usaria repository)
        # self.agent_repository.add(agent)
        
        return agent
    
    def get_agent_by_id(self, agent_id: str, user_id: str) -> Optional[AgentEntity]:
        """
        Busca agente por ID
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            AgentEntity: Agente encontrado ou None
        """
        # Simula busca (em implementação real, usaria repository)
        return None
    
    def get_agent_detail(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """
        Busca agente com detalhes e estatísticas
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            Dict com agent e stats
        """
        # Simula busca (em implementação real, usaria repository)
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        stats = self.get_agent_stats(agent_id, user_id)
        
        return {
            'agent': agent,
            'stats': stats
        }
        
    def list_agents(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> Tuple[List[AgentEntity], int]:
        """
        Lista agentes do usuário
        
        Args:
            user_id: ID do usuário
            page: Página
            size: Tamanho da página
            status: Filtro por status
            
        Returns:
            tuple: (agentes, total)
        """
        # Simula listagem (em implementação real, usaria repository)
        return [], 0
    
    def get_agent_stats(self, agent_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca estatísticas do agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            dict: Estatísticas ou None
        """
        # Simula estatísticas (em implementação real, usaria repository)
        return None
    
    def execute_agent(self, agent_id: str, dto: AgentExecuteRequest, user_id: str) -> Dict[str, Any]:
        """
        Executa agente
        
        Args:
            agent_id: ID do agente
            dto: Dados de execução
            user_id: ID do usuário
            
        Returns:
            dict: Resultado da execução
            
        Raises:
            ValueError: Se agente não encontrado
        """
        # Simula execução
        return {
            'response': f"Resposta simulada para: {dto.message}",
            'execution_time': 0.1,
            'tokens_used': 50
        }
    
    def activate_agent(self, agent_id: str, user_id: str) -> AgentEntity:
        """
        Ativa agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            AgentEntity: Agente ativado
            
        Raises:
            ValueError: Se agente não encontrado
        """
        # Busca agente
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Aplica regra de negócio via Domain
        agent.activate()
        
        # Simula persistência (em implementação real, usaria repository)
        # self.agent_repository.update(agent)
        
        return agent
    
    def deactivate_agent(self, agent_id: str, user_id: str) -> AgentEntity:
        """
        Desativa agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            AgentEntity: Agente desativado
            
        Raises:
            ValueError: Se agente não encontrado
        """
        # Busca agente
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Aplica regra de negócio via Domain
        agent.deactivate()
        
        # Simula persistência (em implementação real, usaria repository)
        # self.agent_repository.update(agent)
        
        return agent
    
    def start_training(self, agent_id: str, user_id: str) -> AgentEntity:
        """
        Inicia treinamento do agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            AgentEntity: Agente em treinamento
            
        Raises:
            ValueError: Se agente não encontrado
        """
        # Busca agente
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Aplica regra de negócio via Domain
        agent.start_training()
        
        # Simula persistência (em implementação real, usaria repository)
        # self.agent_repository.update(agent)
        
        return agent
