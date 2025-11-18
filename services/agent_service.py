"""
Serviço de agentes - Implementação IT Valley
Orquestra casos de uso sem implementar regras de negócio
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from schemas.agents.requests import AgentCreateRequest, AgentUpdateRequest, AgentExecuteRequest
from schemas.agents.responses import AgentResponse, AgentDetailResponse, AgentListResponse
from data.entities.agent_entities import AgentEntity
from data.agent_repository import AgentRepository
from factories.agent_factory import AgentFactory
from mappers.agent_mapper import AgentMapper


class AgentService:
    """
    Serviço de agentes - Orquestrador
    Coordena fluxos sem implementar regras de negócio
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_repository = AgentRepository(db)
    
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
        import uuid
        from datetime import datetime
        
        # 1. Validações básicas
        if not dto.name:
            raise ValueError("Nome do agente é obrigatório")
        
        # 2. Define valores padrão para campos opcionais
        model = dto.model or "gpt-3.5-turbo"
        temperature = dto.temperature if dto.temperature is not None else 0.7
        max_tokens = dto.max_tokens if dto.max_tokens is not None else 1000
        
        # 3. Cria entidade diretamente (sem usar Factory problemático)
        agent = AgentEntity(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=dto.name,
            description=dto.description,
            agent_type=dto.type.value if hasattr(dto.type, 'value') else str(dto.type),
            system_prompt=dto.instructions or dto.system_prompt,
            personality=None,
            avatar_url=None,
            status="active",  # Status ativo ao criar
            llm_provider="openai",
            model=model,
            temperature=str(temperature),
            max_tokens=str(max_tokens),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_used=None,
            usage_count=0
        )
        
        # 4. Persiste no banco
        return self.agent_repository.create_agent(agent)
    
    def get_agent_by_id(self, agent_id: str, user_id: str) -> Optional[AgentEntity]:
        """
        Busca agente por ID
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            AgentEntity: Agente encontrado ou None
        """
        return self.agent_repository.get_agent_by_id(agent_id, user_id)
    
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
        return self.agent_repository.list_agents_by_user(user_id, page, size, status)
    
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
        
        # Persiste no banco de dados
        self.agent_repository.update_agent(agent)
        
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
        
        # Persiste no banco de dados
        self.agent_repository.update_agent(agent)
        
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
        
        # Persiste no banco de dados
        self.agent_repository.update_agent(agent)
        
        return agent
