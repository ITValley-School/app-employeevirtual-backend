"""
Factory principal para agentes
Delega para domain/agents/agent_factory.py
Seguindo padrão IT Valley Architecture
"""
from typing import Optional
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
        """Cria novo agente"""
        return DomainAgentFactory.create_agent(dto)

    @staticmethod
    def name_from(dto: AgentCreateRequest) -> str:
        """Extrai nome de DTO"""
        return DomainAgentFactory.name_from(dto)

    @staticmethod
    def user_id_from(dto: AgentCreateRequest) -> str:
        """Extrai user_id de DTO"""
        return DomainAgentFactory.user_id_from(dto)

    @staticmethod
    def create_from_existing(agent: AgentEntity, updates: AgentUpdateRequest) -> AgentEntity:
        """Cria agente atualizado"""
        return DomainAgentFactory.create_from_existing(agent, updates)

    @staticmethod
    def validate_agent_data(dto: AgentCreateRequest) -> list[str]:
        """Valida dados do agente"""
        return DomainAgentFactory.validate_agent_data(dto)

    # ========== HELPERS PARA EXECUTE DTO ==========

    @staticmethod
    def message_from(dto) -> str:
        """Extrai mensagem do DTO de execução"""
        if hasattr(dto, 'message'):
            return dto.message or ""
        if isinstance(dto, dict):
            return dto.get('message', "")
        return ""

    @staticmethod
    def context_from(dto) -> Optional[dict]:
        """Extrai contexto do DTO de execução"""
        if hasattr(dto, 'context'):
            return dto.context
        if isinstance(dto, dict):
            return dto.get('context')
        return None

    @staticmethod
    def session_id_from(dto) -> Optional[str]:
        """Extrai session_id do DTO de execução"""
        if hasattr(dto, 'session_id'):
            return dto.session_id
        if isinstance(dto, dict):
            return dto.get('session_id')
        return None

    @staticmethod
    def build_message_payload(dto) -> str:
        """Constrói payload de mensagem enriquecido com contexto"""
        message = AgentFactory.message_from(dto)
        context = AgentFactory.context_from(dto)
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            return f"Contexto adicional:\n{context_str}\n\nMensagem do usuário: {message}"
        return message

    @staticmethod
    def has_file_context(dto) -> Optional[dict]:
        """Retorna contexto de arquivo se presente no DTO"""
        context = AgentFactory.context_from(dto)
        if context and context.get('has_file'):
            return context
        return None

    # ========== HELPERS PARA ENTITY ==========

    @staticmethod
    def id_from(agent) -> str:
        """Extrai ID da entidade de agente"""
        return getattr(agent, 'id', '')

    @staticmethod
    def name_from_entity(agent) -> str:
        """Extrai nome da entidade de agente"""
        return getattr(agent, 'name', '')

    @staticmethod
    def get_execution_config(agent) -> dict:
        """Extrai configuração de execução do agente"""
        name = getattr(agent, 'name', 'Agente')
        return {
            'id': getattr(agent, 'id', ''),
            'name': name,
            'model': getattr(agent, 'model', 'gpt-4-turbo-preview'),
            'temperature': float(getattr(agent, 'temperature', 0.7) or 0.7),
            'max_tokens': int(getattr(agent, 'max_tokens', 2000) or 2000),
            'system_prompt': getattr(agent, 'system_prompt', '') or f"Você é o agente {name}. Responda como especialista no assunto.",
        }

    @staticmethod
    def get_default_execution_config() -> dict:
        """Retorna configuração padrão de execução"""
        return {
            'id': '',
            'name': 'Assistente EmployeeVirtual',
            'model': 'gpt-4-turbo-preview',
            'temperature': 0.7,
            'max_tokens': 2000,
            'system_prompt': 'Você é um assistente útil e amigável.',
        }

    @staticmethod
    def build_enriched_message(dto, agent) -> str:
        """Constrói mensagem enriquecida com informações de arquivo"""
        message = AgentFactory.message_from(dto)
        file_context = AgentFactory.has_file_context(dto)
        if file_context:
            file_name = file_context.get('file_name', 'arquivo')
            file_type = file_context.get('file_content_type', '')
            return f"{message}\n\n[Arquivo anexado: {file_name} ({file_type})]"
        return message

    @staticmethod
    def increment_usage(agent) -> None:
        """Incrementa uso do agente (método de domínio via Factory)"""
        from datetime import datetime
        agent.last_used = datetime.utcnow()
        agent.usage_count = str(int(getattr(agent, 'usage_count', '0') or '0') + 1)
        agent.updated_at = datetime.utcnow()

    @staticmethod
    def count_tokens(message: str, response: str) -> int:
        """Conta tokens aproximados"""
        return len((message or "").split()) + len((response or "").split())

    # ========== HELPERS PARA SYSTEM AGENT ==========

    @staticmethod
    def get_system_agent_type(system_agent) -> str:
        """Extrai tipo do agente de sistema (normalizado para lowercase)"""
        agent_type = getattr(system_agent, 'agent_type', '') or ''
        return agent_type.lower()

    @staticmethod
    def get_system_agent_config(system_agent) -> dict:
        """Extrai configuração do agente de sistema"""
        return {
            'name': getattr(system_agent, 'name', ''),
            'system_prompt': getattr(system_agent, 'system_prompt', '') or '',
            'orion_endpoint': getattr(system_agent, 'orion_endpoint', None),
        }
