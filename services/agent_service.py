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
from integrations.ai.vector_db_client import VectorDBClient

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
    
    def __init__(self, db: Session, ai_service: Optional[AIService] = None, vector_db_client: Optional[VectorDBClient] = None):
        self.db = db
        self.agent_repository = AgentRepository(db)
        # Usa singleton para evitar múltiplas inicializações do Pinecone
        self.ai_service = ai_service or AIService.get_instance()
        self.vector_db_client = vector_db_client or VectorDBClient()
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
        
        # Verifica se deve usar RAG
        has_docs = self.agent_document_repository.has_documents(agent.id)
        should_use_rag = self.ai_service.supports_rag and has_docs
        
        logger.info(
            f"🚀 Executando agente {agent.id} ({agent.name}): "
            f"RAG={'✅' if should_use_rag else '❌'} (supports_rag={self.ai_service.supports_rag}, has_docs={has_docs})"
        )
        
        try:
            if should_use_rag:
                logger.info(f"🔎 Usando RAG para agente {agent.id}")
                response_text = self.ai_service.generate_rag_response_sync(
                    message=message_payload,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    instructions=system_prompt
                )
            else:
                logger.info(f"💬 Usando resposta padrão para agente {agent.id}")
                response_text = self.ai_service.generate_response_sync(
                    message=message_payload,
                    system_prompt=system_prompt,
                    agent_id=agent.id,
                    user_id=user_id,
                    temperature=temperature,
                    model=model,
                    max_tokens=max_tokens
                )
            
            if not response_text or len(response_text.strip()) == 0:
                logger.error(f"❌ Resposta vazia do agente {agent.id}")
                response_text = "Desculpe, não consegui gerar uma resposta. Tente novamente."
        except Exception as exc:
            logger.error(
                f"❌ Erro ao executar agente {agent.id}: {str(exc)}",
                exc_info=True
            )
            response_text = f"Erro ao processar sua mensagem: {str(exc)}"
        
        execution_time = time.perf_counter() - start_time
        logger.info(
            f"✅ Agente {agent.id} executado em {execution_time:.3f}s. "
            f"Resposta: {len(response_text)} caracteres"
        )
        
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
            'rag_used': should_use_rag
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

        metadata.update({
            "agent_id": agent_id,
            "user_id": user_id,
            "agent_name": agent.name,
        })

        metadata_json = json.dumps(metadata)

        final_file_name = file_name or f"{agent_id}.pdf"
        vector_response = self.vector_db_client.upload_pdf(
            file_name=final_file_name,
            content=file_content,
            content_type=content_type,
            namespace=agent_id,  # Usa agent_id como namespace
            metadata_json=metadata_json,
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
