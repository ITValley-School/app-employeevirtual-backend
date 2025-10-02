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
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            type=agent.type,
            status=agent.status,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
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
        return AgentDetailResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            type=agent.type,
            status=agent.status,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            user_id=agent.user_id,
            instructions=agent.instructions,
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
