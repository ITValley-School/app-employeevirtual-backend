"""
Factory principal para agentes
Delega para domain/agents/agent_factory.py
Seguindo padrão IT Valley Architecture
"""
from domain.agents.agent_factory import AgentFactory as DomainAgentFactory
from schemas.agents.requests import AgentCreateRequest, AgentUpdateRequest
from domain.agents.agent_entity import AgentEntity


class AgentFactory:
    """
    Factory principal para agentes
    Delega para factory do domínio
    """
    
    @staticmethod
    def create_agent(dto: AgentCreateRequest) -> AgentEntity:
        """
        Cria novo agente
        
        Args:
            dto: Dados para criação
            
        Returns:
            AgentEntity: Agente criado
        """
        return DomainAgentFactory.create_agent(dto)
    
    @staticmethod
    def name_from(dto: AgentCreateRequest) -> str:
        """
        Extrai nome de DTO
        
        Args:
            dto: Dados de criação
            
        Returns:
            str: Nome extraído
        """
        return DomainAgentFactory.name_from(dto)
    
    @staticmethod
    def user_id_from(dto: AgentCreateRequest) -> str:
        """
        Extrai user_id de DTO
        
        Args:
            dto: Dados de criação
            
        Returns:
            str: User ID extraído
        """
        return DomainAgentFactory.user_id_from(dto)
    
    @staticmethod
    def create_from_existing(agent: AgentEntity, updates: AgentUpdateRequest) -> AgentEntity:
        """
        Cria agente atualizado
        
        Args:
            agent: Agente existente
            updates: Atualizações
            
        Returns:
            AgentEntity: Agente atualizado
        """
        return DomainAgentFactory.create_from_existing(agent, updates)
    
    @staticmethod
    def validate_agent_data(dto: AgentCreateRequest) -> list[str]:
        """
        Valida dados do agente
        
        Args:
            dto: Dados para validação
            
        Returns:
            list[str]: Lista de erros encontrados
        """
        return DomainAgentFactory.validate_agent_data(dto)
