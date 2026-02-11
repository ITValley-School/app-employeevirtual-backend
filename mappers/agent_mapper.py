"""
Mapper para agentes
Converte entre Entity (domínio) e Response (API)
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from schemas.agents.responses import (
    AgentResponse,
    AgentDetailResponse,
    AgentListResponse,
    AgentExecuteResponse,
    AgentStatsResponse,
    AgentDocumentResponse,
    AgentDocumentListResponse,
    AgentDocumentDeleteResponse,
    SystemAgentResponse,
    SystemAgentListResponse
)
from data.entities.agent_entities import AgentEntity
from data.entities.system_agent_entities import SystemAgentEntity


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
    def to_execution_response(result: dict, agent_id: str) -> AgentExecuteResponse:
        """
        Cria response para execução de agente a partir de dict do Service

        Args:
            result: Dict completo retornado pelo Service
            agent_id: ID do agente

        Returns:
            AgentExecuteResponse: Response de execução
        """
        return AgentExecuteResponse(
            agent_id=agent_id,
            message=result.get('message', ''),
            response=result.get('response', ''),
            execution_time=result.get('execution_time', 0.0),
            tokens_used=result.get('tokens_used', 0),
            session_id=result.get('session_id'),
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
    
    # ========== MÉTODOS PARA DOCUMENTOS ==========

    @staticmethod
    def to_document(doc: Dict[str, Any], agent_id: str, user_id: str) -> AgentDocumentResponse:
        """
        Converte dict de documento para AgentDocumentResponse

        Args:
            doc: Dicionário com dados do documento
            agent_id: ID do agente
            user_id: ID do usuário

        Returns:
            AgentDocumentResponse: Documento formatado para API
        """
        created_at = doc.get("created_at")
        if not created_at:
            created_at = datetime.utcnow()

        return AgentDocumentResponse(
            id=doc.get("id", str(doc.get("_id", ""))),
            agent_id=doc.get("agent_id", agent_id),
            user_id=doc.get("user_id", user_id),
            file_name=doc.get("file_name", ""),
            metadata=doc.get("metadata", {}),
            vector_response=doc.get("vector_response"),
            created_at=created_at,
            updated_at=doc.get("updated_at"),
            mongo_error=doc.get("mongo_error", False)
        )

    @staticmethod
    def to_document_list(
        documents: List[Dict[str, Any]], agent_id: str, user_id: str
    ) -> AgentDocumentListResponse:
        """
        Converte lista de documentos para AgentDocumentListResponse

        Args:
            documents: Lista de dicts de documentos
            agent_id: ID do agente
            user_id: ID do usuário

        Returns:
            AgentDocumentListResponse: Lista formatada para API
        """
        document_responses = [
            AgentMapper.to_document(doc, agent_id, user_id) for doc in documents
        ]
        return AgentDocumentListResponse(
            documents=document_responses,
            total=len(document_responses),
            agent_id=agent_id
        )

    @staticmethod
    def to_document_delete(result: Dict[str, Any], document_id: str) -> AgentDocumentDeleteResponse:
        """
        Converte resultado de deleção para AgentDocumentDeleteResponse

        Args:
            result: Dict com resultado da operação de deleção
            document_id: ID do documento

        Returns:
            AgentDocumentDeleteResponse: Resultado formatado para API
        """
        return AgentDocumentDeleteResponse(
            success=result.get("success", True),
            document_id=result.get("document_id", document_id),
            file_name=result.get("file_name"),
            vector_db_response=result.get("vector_db_response"),
            mongo_deleted=result.get("mongo_deleted", True),
            message="Documento removido com sucesso"
        )

    @staticmethod
    def to_upload_response(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte resultado de upload para response formatado

        Args:
            result: Dict com resultado do upload

        Returns:
            Dict formatado para API
        """
        document = result.get("document", {})
        if document.get("mongo_error"):
            return {
                "message": "Documento enviado com sucesso para Vector DB. Aviso: falha ao registrar no MongoDB.",
                "document": document,
                "vector_db_response": result.get("vector_db_response"),
                "warning": "MongoDB indisponível, mas documento está no Vector DB"
            }

        return {
            "message": "Documento enviado com sucesso",
            "document": document,
            "vector_db_response": result.get("vector_db_response")
        }

    # ========== MÉTODOS PARA AGENTES DE SISTEMA ==========
    
    @staticmethod
    def to_system_agent(system_agent: SystemAgentEntity) -> SystemAgentResponse:
        """
        Converte SystemAgentEntity para SystemAgentResponse
        
        Args:
            system_agent: Entidade de agente de sistema
            
        Returns:
            SystemAgentResponse: Dados do agente de sistema
        """
        return SystemAgentResponse(
            id=system_agent.id,
            name=system_agent.name,
            description=system_agent.description,
            agent_type=system_agent.agent_type,
            system_prompt=system_agent.system_prompt,
            avatar_url=system_agent.avatar_url,
            orion_endpoint=system_agent.orion_endpoint,
            is_active=system_agent.is_active,
            created_at=system_agent.created_at,
            updated_at=system_agent.updated_at
        )
    
    @staticmethod
    def to_system_agent_list(system_agents: List[SystemAgentEntity]) -> SystemAgentListResponse:
        """
        Converte lista de SystemAgentEntity para SystemAgentListResponse
        
        Args:
            system_agents: Lista de agentes de sistema
            
        Returns:
            SystemAgentListResponse: Lista formatada para API
        """
        return SystemAgentListResponse(
            agents=[AgentMapper.to_system_agent(agent) for agent in system_agents],
            total=len(system_agents)
        )
