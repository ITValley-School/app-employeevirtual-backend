"""
Serviço de agentes - Implementação IT Valley
Orquestra casos de uso sem implementar regras de negócio
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
import logging
import time
from datetime import datetime
import json

from schemas.agents.requests import AgentCreateRequest, AgentUpdateRequest, AgentExecuteRequest
from data.entities.agent_entities import AgentEntity
from data.agent_repository import AgentRepository
from data.agent_document_repository import AgentDocumentRepository
from factories.agent_factory import AgentFactory
from mappers.agent_mapper import AgentMapper
from services.ai_service import AIService
from integrations.ai.vector_store_service import VectorStoreService
from config.settings import settings

logger = logging.getLogger(__name__)


def _normalize_model_name(model: Optional[str]) -> str:
    """
    Normaliza nomes de modelos para o formato esperado pelo Pydantic AI
    """
    if not model:
        return "gpt-4-turbo-preview"
    model = model.strip()
    if model.startswith("openai:"):
        return model[7:]
    return model


class AgentService:
    """
    Serviço de agentes - Orquestrador
    Coordena fluxos sem implementar regras de negócio
    """
    
    def __init__(self, db: Session, ai_service: Optional[AIService] = None, vector_db_client: Optional[VectorStoreService] = None):
        self.db = db
        self.agent_repository = AgentRepository(db)
        self.ai_service = ai_service or AIService()
        self.vector_store: Optional[VectorStoreService] = None
        if vector_db_client:
            self.vector_store = vector_db_client
        elif settings.openai_api_key and settings.pinecone_api_key and settings.pinecone_index_name:
            try:
                self.vector_store = VectorStoreService(settings.pinecone_index_name)
            except ValueError as exc:
                logger.warning("VectorStoreService indisponível: %s", exc)
        self.agent_document_repository = AgentDocumentRepository()
    
    def create_agent(self, dto: AgentCreateRequest, user_id: str) -> AgentEntity:
        """
        Cria novo agente utilizando a Factory do domínio
        """
        payload = dto.model_dump()
        payload["user_id"] = user_id
        
        domain_agent = AgentFactory.create_agent(payload)
        
        agent = AgentEntity(
            id=domain_agent.id,
            user_id=domain_agent.user_id,
            name=domain_agent.name,
            description=domain_agent.description,
            agent_type=domain_agent.type,
            system_prompt=domain_agent.system_prompt or domain_agent.instructions,
            personality=None,
            avatar_url=None,
            status=domain_agent.status,
            llm_provider="openai",
            model=domain_agent.model,
            temperature=str(domain_agent.temperature),
            max_tokens=str(domain_agent.max_tokens),
            created_at=domain_agent.created_at,
            updated_at=domain_agent.created_at,
            last_used=None,
            usage_count=0
        )
        
        stored_agent = self.agent_repository.create_agent(agent)

        if self.vector_store:
            try:
                self.vector_store.ensure_namespace(stored_agent.id)
            except Exception as exc:
                logger.error("Erro ao criar namespace no Pinecone: %s", exc, exc_info=True)

        return stored_agent
    
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
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        system_prompt = agent.system_prompt or f"Você é o agente {agent.name}. Responda como especialista no assunto."
        
        message_payload = dto.message
        if dto.context:
            context_str = "\n".join([f"{key}: {value}" for key, value in dto.context.items()])
            message_payload = f"Contexto adicional:\n{context_str}\n\nMensagem do usuário: {dto.message}"
        
        model = _normalize_model_name(agent.model)
        temperature = float(agent.temperature or 0.7)
        max_tokens = int(agent.max_tokens or 2000)
        
        start_time = time.perf_counter()
        rag_supported = self.ai_service.supports_rag
        has_docs = self.agent_document_repository.has_documents(agent.id, user_id)
        logger.info(
            "RAG check for agent %s | supports_rag=%s | has_docs=%s",
            agent.id,
            rag_supported,
            has_docs,
        )

        should_use_rag = rag_supported and has_docs

        if should_use_rag:
            response_text = self.ai_service.generate_rag_response_sync(
                message=message_payload,
                agent_id=agent.id,
                agent_name=agent.name,
                instructions=system_prompt
            )
        else:
            if not rag_supported:
                logger.warning("RAG desabilitado para o agente %s (variáveis ausentes?)", agent.id)
            elif not has_docs:
                logger.warning("Agente %s não possui documentos para RAG", agent.id)
            response_text = self.ai_service.generate_response_sync(
                message=message_payload,
                system_prompt=system_prompt,
                agent_id=agent.id,
                user_id=user_id,
                temperature=temperature,
                model=model,
                max_tokens=max_tokens
            )
        execution_time = time.perf_counter() - start_time
        
        tokens_used = len((dto.message or "").split()) + len(response_text.split())
        
        now = datetime.utcnow()
        agent.last_used = now
        agent.usage_count = str(int(agent.usage_count or "0") + 1)
        agent.updated_at = now
        self.agent_repository.update_agent(agent)
        
        return {
            'response': response_text,
            'message': dto.message,
            'execution_time': round(execution_time, 4),
            'tokens_used': tokens_used,
            'session_id': dto.session_id,
            'rag_used': should_use_rag,
        }

    def upload_agent_document(
        self,
        agent_id: str,
        user_id: str,
        file_content: bytes,
        file_name: str,
        content_type: Optional[str],
        metadata_raw: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia um PDF associado ao agente para o serviço vetorial externo.
        """
        if not file_content:
            raise ValueError("Arquivo PDF não pode estar vazio")

        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")

        metadata: Dict[str, Any] = {}
        if metadata_raw:
            try:
                metadata = json.loads(metadata_raw)
            except json.JSONDecodeError as exc:
                raise ValueError("Metadados inválidos. Envie um JSON válido.") from exc

        metadata = metadata or {}
        metadata.setdefault("agent_id", agent_id)
        metadata.setdefault("user_id", user_id)
        metadata.setdefault("agent_name", agent.name)

        metadata_json = json.dumps(metadata)

        final_file_name = file_name or f"{agent_id}.pdf"
        if not self.vector_store:
            raise ValueError(
                "Serviço vetorial não configurado. Defina OPENAI_API_KEY e variáveis do Pinecone para habilitar o RAG."
            )

        vector_response = self.vector_store.upsert_pdf(
            agent_id=agent_id,
            user_id=user_id,
            file_name=final_file_name,
            file_content=file_content,
            metadata=metadata,
        )

        stored_document = self.agent_document_repository.record_upload(
            agent_id=agent_id,
            user_id=user_id,
            file_name=final_file_name,
            metadata=metadata,
            vector_response=vector_response,
        )

        return {
            "vector_db_response": vector_response,
            "document": stored_document,
        }

    def list_agent_documents(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Retorna documentos vetoriais do agente."""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        return self.agent_document_repository.list_documents(agent_id, user_id)

    def delete_agent_document(self, agent_id: str, document_id: str, user_id: str) -> bool:
        """Remove documento associado ao agente."""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")

        document = self.agent_document_repository.get_document(document_id, user_id)
        if not document or document.get("agent_id") != agent_id:
            raise ValueError("Documento não encontrado")

        deleted = self.agent_document_repository.delete_document(document_id, user_id)
        if not deleted:
            raise ValueError("Não foi possível remover o documento")
        return deleted
    
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
