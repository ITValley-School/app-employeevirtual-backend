"""
Factory para agentes
Única porta de entrada para criação de entidades
Seguindo padrão IT Valley Architecture
"""
from typing import Any
from datetime import datetime
from uuid import uuid4

from domain.agents.agent_entity import AgentEntity
from schemas.agents.requests import AgentCreateRequest


class AgentFactory:
    """
    Factory para criação de agentes
    Centraliza validações e criação de entidades
    """
    
    @staticmethod
    def create_agent(dto: Any) -> AgentEntity:
        """
        Cria nova entidade de agente
        
        Args:
            dto: Dados para criação (AgentCreateRequest, dict, etc.)
            
        Returns:
            AgentEntity: Entidade criada
            
        Raises:
            ValueError: Se dados inválidos
        """
        # Helper para extrair dados de forma segura
        def _get(data: Any, key: str, default=None):
            if hasattr(data, key):
                return getattr(data, key)
            elif isinstance(data, dict):
                return data.get(key, default)
            return default
        
        # Extrai dados
        name = _get(dto, "name")
        description = _get(dto, "description")
        type_agent = _get(dto, "type")
        instructions = _get(dto, "instructions")
        model = _get(dto, "model", "gpt-3.5-turbo")
        temperature = _get(dto, "temperature", 0.7)
        max_tokens = _get(dto, "max_tokens", 1000)
        system_prompt = _get(dto, "system_prompt")
        user_id = _get(dto, "user_id", "")
        
        # Validações básicas
        if not name or len(name.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        if not instructions or len(instructions.strip()) < 10:
            raise ValueError("Instruções devem ter pelo menos 10 caracteres")
        
        if not type_agent:
            raise ValueError("Tipo do agente é obrigatório")
        
        # Valida temperatura
        if temperature < 0.0 or temperature > 2.0:
            raise ValueError("Temperatura deve estar entre 0.0 e 2.0")
        
        # Valida max_tokens
        if max_tokens < 100 or max_tokens > 4000:
            raise ValueError("Max tokens deve estar entre 100 e 4000")
        
        # Cria entidade
        return AgentEntity(
            id=uuid4().hex,
            name=name.strip(),
            description=description.strip() if description else None,
            type=type_agent,
            instructions=instructions.strip(),
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt.strip() if system_prompt else None,
            user_id=user_id,
            status="active",
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def name_from(dto: Any) -> str:
        """
        Helper para extrair nome de DTO
        
        Args:
            dto: Dados (AgentCreateRequest, dict, etc.)
            
        Returns:
            str: Nome extraído
        """
        if hasattr(dto, "name"):
            return dto.name
        elif isinstance(dto, dict):
            return dto.get("name", "")
        return ""
    
    @staticmethod
    def id_from(dto: Any) -> str:
        """
        Helper para extrair ID de DTO
        
        Args:
            dto: Dados (AgentResponse, dict, etc.)
            
        Returns:
            str: ID extraído
        """
        if hasattr(dto, "id"):
            return dto.id
        elif isinstance(dto, dict):
            return dto.get("id", "")
        return ""
    
    @staticmethod
    def user_id_from(dto: Any) -> str:
        """
        Helper para extrair user_id de DTO
        
        Args:
            dto: Dados (AgentCreateRequest, dict, etc.)
            
        Returns:
            str: User ID extraído
        """
        if hasattr(dto, "user_id"):
            return dto.user_id
        elif isinstance(dto, dict):
            return dto.get("user_id", "")
        return ""
    
    @staticmethod
    def create_from_existing(agent: AgentEntity, updates: Any) -> AgentEntity:
        """
        Cria nova entidade baseada em existente com atualizações
        
        Args:
            agent: Agente existente
            updates: Dados para atualização
            
        Returns:
            AgentEntity: Nova entidade atualizada
        """
        # Cria cópia
        updated_agent = AgentEntity(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            type=agent.type,
            status=agent.status,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            instructions=agent.instructions,
            system_prompt=agent.system_prompt,
            user_id=agent.user_id,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
        
        # Aplica atualizações
        updated_agent.apply_update_from_any(updates)
        
        return updated_agent
    
    @staticmethod
    def validate_agent_data(dto: Any) -> list[str]:
        """
        Valida dados do agente
        
        Args:
            dto: Dados para validação
            
        Returns:
            list[str]: Lista de erros encontrados
        """
        errors = []
        
        # Helper para extrair dados
        def _get(data: Any, key: str, default=None):
            if hasattr(data, key):
                return getattr(data, key)
            elif isinstance(data, dict):
                return data.get(key, default)
            return default
        
        name = _get(dto, "name")
        if not name or len(name.strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
        
        instructions = _get(dto, "instructions")
        if not instructions or len(instructions.strip()) < 10:
            errors.append("Instruções devem ter pelo menos 10 caracteres")
        
        type_agent = _get(dto, "type")
        if not type_agent:
            errors.append("Tipo do agente é obrigatório")
        
        temperature = _get(dto, "temperature", 0.7)
        if temperature < 0.0 or temperature > 2.0:
            errors.append("Temperatura deve estar entre 0.0 e 2.0")
        
        max_tokens = _get(dto, "max_tokens", 1000)
        if max_tokens < 100 or max_tokens > 4000:
            errors.append("Max tokens deve estar entre 100 e 4000")
        
        return errors
