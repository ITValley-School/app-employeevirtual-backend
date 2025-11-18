"""
Mapper para agentes
Converte entre Entity (domínio) e Response (API)
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List
from datetime import datetime

from schemas.agents.responses import (
    AgentResponse, 
    AgentDetailResponse, 
    AgentListResponse,
    AgentExecuteResponse,
    AgentStatsResponse
)
from data.entities.agent_entities import AgentEntity


class AgentMapper:
    """Mapper para conversão de agentes"""
    
    @staticmethod
    def to_public(agent: AgentEntity) -> AgentResponse:
        """
        Converte AgentEntity para AgentResponse (visão pública)
        
        Args:
            agent: Entidade do domínio
            
        Returns:
            AgentResponse: Dados públicos do agente
        """
        from schemas.agents.responses import AgentType, AgentStatus
        
        # Parsear o tipo
        agent_type = getattr(agent, 'agent_type', 'chatbot')
        try:
            type_enum = AgentType[agent_type.upper()] if agent_type else AgentType.CHATBOT
        except (KeyError, AttributeError):
            type_enum = AgentType.CHATBOT
        
        # Parsear o status
        agent_status = getattr(agent, 'status', 'inactive') or 'inactive'
        try:
            status_enum = AgentStatus[agent_status.upper()] if agent_status else AgentStatus.INACTIVE
        except (KeyError, AttributeError):
            status_enum = AgentStatus.INACTIVE
        
        # Handle NULL datetime values with default
        created_at = agent.created_at if agent.created_at else datetime.utcnow()
        updated_at = agent.updated_at if agent.updated_at else created_at
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            type=type_enum,
            status=status_enum,
            model=agent.model or "gpt-4",
            temperature=float(agent.temperature or 0.7),
            max_tokens=int(agent.max_tokens or 4096),
            created_at=created_at,
            updated_at=updated_at,
            user_id=agent.user_id
        )
    
    @staticmethod
    def to_detail(agent: AgentEntity, stats: Optional[dict] = None) -> AgentDetailResponse:
        """
        Converte AgentEntity para AgentDetailResponse (visão detalhada)
        
        Args:
            agent: Entidade do domínio
            stats: Estatísticas opcionais do agente
            
        Returns:
            AgentDetailResponse: Dados detalhados do agente
        """
        from schemas.agents.responses import AgentType, AgentStatus
        
        # Parsear o tipo
        agent_type = getattr(agent, 'agent_type', 'chatbot')
        try:
            type_enum = AgentType[agent_type.upper()] if agent_type else AgentType.CHATBOT
        except (KeyError, AttributeError):
            type_enum = AgentType.CHATBOT
        
        # Parsear o status
        agent_status = getattr(agent, 'status', 'inactive') or 'inactive'
        try:
            status_enum = AgentStatus[agent_status.upper()] if agent_status else AgentStatus.INACTIVE
        except (KeyError, AttributeError):
            status_enum = AgentStatus.INACTIVE
        
        # Handle NULL datetime values with default
        created_at = agent.created_at if agent.created_at else datetime.utcnow()
        updated_at = agent.updated_at if agent.updated_at else created_at
        
        return AgentDetailResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            type=type_enum,
            status=status_enum,
            model=agent.model or "gpt-4",
            temperature=float(agent.temperature or 0.7),
            max_tokens=int(agent.max_tokens or 4096),
            created_at=created_at,
            updated_at=updated_at,
            user_id=agent.user_id,
            instructions=getattr(agent, 'system_prompt', '') or '',
            system_prompt=agent.system_prompt,
            total_executions=stats.get('total_executions', 0) if stats else 0,
            last_execution=stats.get('last_execution') if stats else None,
            performance_score=stats.get('performance_score') if stats else None
        )
    
    @staticmethod
    def to_list(agents: List[AgentEntity], total: int, page: int, size: int) -> AgentListResponse:
        """
        Converte lista de AgentEntity para AgentListResponse
        
        Args:
            agents: Lista de entidades do domínio
            total: Total de agentes
            page: Página atual
            size: Tamanho da página
            
        Returns:
            AgentListResponse: Lista formatada para API
        """
        return AgentListResponse(
            agents=[AgentMapper.to_public(agent) for agent in agents],
            total=total,
            page=page,
            size=size
        )
    
    @staticmethod
    def to_execution_response(
        agent_id: str, 
        message: str, 
        response: str, 
        execution_time: float,
        tokens_used: int,
        session_id: Optional[str] = None
    ) -> AgentExecuteResponse:
        """
        Cria response para execução de agente
        
        Args:
            agent_id: ID do agente
            message: Mensagem enviada
            response: Resposta do agente
            execution_time: Tempo de execução
            tokens_used: Tokens utilizados
            session_id: ID da sessão
            
        Returns:
            AgentExecuteResponse: Response de execução
        """
        return AgentExecuteResponse(
            agent_id=agent_id,
            message=message,
            response=response,
            execution_time=execution_time,
            tokens_used=tokens_used,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def to_stats(agent: AgentEntity, stats: dict) -> AgentStatsResponse:
        """
        Converte AgentEntity para AgentStatsResponse (estatísticas)
        
        Args:
            agent: Entidade do domínio
            stats: Estatísticas do agente
            
        Returns:
            AgentStatsResponse: Estatísticas formatadas
        """
        return AgentStatsResponse(
            agent_id=agent.id,
            total_executions=stats.get('total_executions', 0),
            avg_execution_time=stats.get('avg_execution_time', 0.0),
            total_tokens_used=stats.get('total_tokens_used', 0),
            success_rate=stats.get('success_rate', 0.0),
            last_activity=stats.get('last_activity'),
            performance_trend=stats.get('performance_trend', 'stable')
        )
    
    @staticmethod
    def to_display(agent: AgentEntity) -> dict:
        """
        Converte AgentEntity para formato de exibição simples
        
        Args:
            agent: Entidade do domínio
            
        Returns:
            dict: Dados para exibição (nome e tipo apenas)
        """
        return {
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "status": agent.status
        }
