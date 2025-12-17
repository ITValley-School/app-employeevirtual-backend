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
import threading

from schemas.agents.requests import AgentCreateRequest, AgentUpdateRequest, AgentExecuteRequest
from data.entities.agent_entities import AgentEntity
from data.entities.system_agent_entities import SystemAgentEntity
from data.agent_repository import AgentRepository
from data.system_agent_repository import SystemAgentRepository
from data.agent_document_repository import AgentDocumentRepository
from data.chat_mongodb_repository import ChatMongoDBRepository
from data.system_agent_execution_repository import SystemAgentExecutionRepository
from data.tool_cache_repository import ToolCacheRepository
from factories.agent_factory import AgentFactory
from mappers.agent_mapper import AgentMapper
from services.ai_service import AIService
from integrations.ai.vector_db_client import VectorDBClient
from integrations.ai.orion_client import OrionClient
from integrations.ai.system_agent_tools import build_system_agent, SystemAgentDependencies
from domain.agents.agent_tools import ToolType
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
    
    def __init__(self, db: Session, ai_service: Optional[AIService] = None, vector_db_client: Optional[VectorDBClient] = None):
        self.db = db
        self.agent_repository = AgentRepository(db)
        self.system_agent_repository = SystemAgentRepository(db)
        # Usa singleton para evitar múltiplas inicializações do Pinecone
        self.ai_service = ai_service or AIService.get_instance()
        self.vector_db_client = vector_db_client or VectorDBClient()
        self.agent_document_repository = AgentDocumentRepository()
        # MongoDB repository para salvar conversas (opcional, não bloqueante)
        self.chat_mongodb_repository = ChatMongoDBRepository()
        # Repositórios para agentes de sistema
        self.system_execution_repository = SystemAgentExecutionRepository()
        self.tool_cache_repository = ToolCacheRepository()
    
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
        
        try:
            if should_use_rag:
                logger.info(f"🚀 Executando agente {agent.id} ({agent.name}) com RAG")
                response_text = self.ai_service.generate_rag_response_sync(
                    message=message_payload,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    instructions=system_prompt
                )
            else:
                logger.info(f"🚀 Executando agente {agent.id} ({agent.name})")
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
        logger.info(f"✅ Agente {agent.id} executado em {execution_time:.3f}s")
        
        tokens_used = len((dto.message or "").split()) + len(response_text.split())
        
        now = datetime.utcnow()
        agent.last_used = now
        agent.usage_count = str(int(agent.usage_count or "0") + 1)
        agent.updated_at = now
        self.agent_repository.update_agent(agent)
        
        # Prepara resposta (retorna imediatamente, sem esperar MongoDB)
        result = {
            'response': response_text,
            'message': dto.message,
            'execution_time': round(execution_time, 4),
            'tokens_used': tokens_used,
            'session_id': dto.session_id,
            'rag_used': should_use_rag
        }
        
        # Salva no MongoDB de forma assíncrona (não bloqueante) se tiver session_id
        if dto.session_id:
            self._save_conversation_async(
                session_id=dto.session_id,
                user_id=user_id,
                agent_id=agent.id,
                user_message=dto.message,
                assistant_message=response_text
            )
        
        return result
    
    def _save_conversation_async(self, session_id: str, user_id: str, agent_id: str, 
                                  user_message: str, assistant_message: str):
        """
        Salva conversa no MongoDB de forma assíncrona (não bloqueante).
        Executa em thread separada para não atrasar a resposta ao frontend.
        """
        def save_in_background():
            try:
                # Salva mensagem do usuário
                self.chat_mongodb_repository.add_message({
                    'session_id': session_id,
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'message': user_message,
                    'sender': 'user',
                    'context': {},
                    'metadata': {
                        'created_at': datetime.utcnow(),
                        'source': 'agent_execute'
                    }
                })
                
                # Salva resposta do assistente
                self.chat_mongodb_repository.add_message({
                    'session_id': session_id,
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'message': assistant_message,
                    'sender': 'assistant',
                    'context': {},
                    'metadata': {
                        'created_at': datetime.utcnow(),
                        'source': 'agent_execute'
                    }
                })
                
                logger.debug(f"✅ Conversa salva no MongoDB (background): {session_id}")
            except Exception as e:
                # Não loga erro como crítico - é apenas persistência opcional
                logger.debug(f"⚠️ Falha ao salvar conversa no MongoDB (não crítico): {str(e)}")
        
        # Executa em thread separada (não bloqueia resposta)
        thread = threading.Thread(target=save_in_background, daemon=True)
        thread.start()

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

    def list_agent_documents(
        self,
        agent_id: str,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Lista documentos associados a um agente.
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            Lista de documentos com metadados
        """
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        documents = self.agent_document_repository.list_documents(agent_id, user_id)
        return documents

    def delete_agent_document(
        self,
        agent_id: str,
        document_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Remove um documento do agente (MongoDB + Pinecone).
        
        Args:
            agent_id: ID do agente
            document_id: ID do documento no MongoDB
            user_id: ID do usuário
            
        Returns:
            Dict com resultado da operação
        """
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Busca documento no MongoDB para obter file_name
        document = self.agent_document_repository.get_document_by_id(document_id, user_id)
        if not document:
            raise ValueError("Documento não encontrado")
        
        if document.get("agent_id") != agent_id:
            raise ValueError("Documento não pertence a este agente")
        
        file_name = document.get("file_name")
        namespace = agent_id
        
        # Tenta deletar do Pinecone primeiro
        vector_delete_result = None
        try:
            if file_name:
                vector_delete_result = self.vector_db_client.delete_document(
                    namespace=namespace,
                    file_name=file_name,
                    delete_all=False
                )
            else:
                # Se não tiver file_name, tenta deletar todo o namespace (menos comum)
                logger.warning(f"⚠️ Documento {document_id} não tem file_name, pulando delete no Pinecone")
        except Exception as e:
            logger.warning(
                f"⚠️ Erro ao deletar documento do Pinecone (continuando com delete do MongoDB): {str(e)}"
            )
            # Continua mesmo se falhar no Pinecone
        
        # Deleta do MongoDB
        mongo_deleted = self.agent_document_repository.delete_document(document_id, user_id)
        
        if not mongo_deleted:
            raise ValueError("Erro ao deletar documento do MongoDB")
        
        return {
            "success": True,
            "document_id": document_id,
            "file_name": file_name,
            "vector_db_response": vector_delete_result,
            "mongo_deleted": mongo_deleted,
        }

    def update_agent_document_metadata(
        self,
        agent_id: str,
        document_id: str,
        user_id: str,
        metadata_updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Atualiza metadados de um documento do agente.
        
        Args:
            agent_id: ID do agente
            document_id: ID do documento
            user_id: ID do usuário
            metadata_updates: Dicionário com atualizações de metadados
            
        Returns:
            Dict com documento atualizado
        """
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Busca documento atual
        document = self.agent_document_repository.get_document_by_id(document_id, user_id)
        if not document:
            raise ValueError("Documento não encontrado")
        
        if document.get("agent_id") != agent_id:
            raise ValueError("Documento não pertence a este agente")
        
        # Merge dos metadados existentes com as atualizações
        current_metadata = document.get("metadata", {})
        updated_metadata = {**current_metadata, **metadata_updates}
        
        # Atualiza no MongoDB
        updated_document = self.agent_document_repository.update_document_metadata(
            document_id=document_id,
            user_id=user_id,
            metadata_updates=updated_metadata
        )
        
        if not updated_document:
            raise ValueError("Erro ao atualizar metadados do documento")
        
        return {
            "success": True,
            "document": updated_document,
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
    
    # ========== MÉTODOS PARA AGENTES DE SISTEMA ==========
    
    def get_system_agents(self) -> List[SystemAgentEntity]:
        """
        Lista todos os agentes de sistema ativos
        
        Returns:
            Lista de agentes de sistema
        """
        return self.system_agent_repository.list_all()
    
    def get_system_agent_by_id(self, agent_id: str) -> Optional[SystemAgentEntity]:
        """
        Busca agente de sistema por ID
        
        Args:
            agent_id: ID do agente de sistema
            
        Returns:
            SystemAgentEntity: Agente encontrado ou None
        """
        return self.system_agent_repository.get_by_id(agent_id)
    
    def get_system_agents_by_type(self, agent_type: str) -> List[SystemAgentEntity]:
        """
        Lista agentes de sistema por tipo
        
        Args:
            agent_type: Tipo do agente
            
        Returns:
            Lista de agentes de sistema
        """
        return self.system_agent_repository.get_by_type(agent_type)
    
    def _get_tools_for_system_agent(self, system_agent: SystemAgentEntity) -> List[str]:
        """
        Determina ferramentas disponíveis baseado no tipo do agente
        
        Args:
            system_agent: Agente de sistema
            
        Returns:
            Lista de ferramentas habilitadas
        """
        # Mapeamento de tipos de agente para ferramentas
        tools_mapping = {
            "transcriber": [ToolType.TRANSCRIBE_AUDIO, ToolType.TRANSCRIBE_YOUTUBE],
            "ocr": [ToolType.OCR_IMAGE],
            "document_processor": [ToolType.PROCESS_PDF, ToolType.EXTRACT_TEXT],
            "assistant": [ToolType.TRANSCRIBE_AUDIO, ToolType.OCR_IMAGE, ToolType.PROCESS_PDF],
        }
        
        # Retorna ferramentas baseado no agent_type
        agent_type_lower = system_agent.agent_type.lower() if system_agent.agent_type else ""
        return tools_mapping.get(agent_type_lower, [])
    
    def execute_system_agent(
        self,
        system_agent_id: str,
        dto: AgentExecuteRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Executa agente de sistema com ferramentas avançadas
        
        Args:
            system_agent_id: ID do agente de sistema
            dto: Dados de execução
            user_id: ID do usuário
            
        Returns:
            Dict com resultado da execução
            
        Raises:
            ValueError: Se agente não encontrado
        """
        import time
        start_time = time.perf_counter()
        
        # Busca agente de sistema
        system_agent = self.get_system_agent_by_id(system_agent_id)
        if not system_agent:
            raise ValueError("Agente de sistema não encontrado ou inativo")
        
        logger.info(f"🚀 Executando agente de sistema: {system_agent.name} ({system_agent_id})")
        
        # Determina ferramentas habilitadas
        enabled_tools = self._get_tools_for_system_agent(system_agent)
        logger.info(f"🔧 Ferramentas habilitadas: {enabled_tools}")
        
        # Cria cliente Orion (usa endpoint específico do agente ou fallback)
        orion_client = None
        if enabled_tools:  # Só cria se tiver ferramentas que precisam do Orion
            orion_url = system_agent.orion_endpoint or settings.orion_api_url
            if orion_url:
                try:
                    orion_client = OrionClient(base_url=orion_url)
                    logger.info(f"✅ Cliente Orion inicializado: {orion_url}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao inicializar Orion: {e}")
            else:
                logger.warning("⚠️ Orion não configurado. Ferramentas avançadas não estarão disponíveis.")
        
        # Constrói agente com ferramentas
        system_agent_instance = build_system_agent(
            system_prompt=system_agent.system_prompt,
            enabled_tools=enabled_tools,
            orion_client=orion_client
        )
        
        # Prepara dependências (inclui contexto do arquivo se houver)
        file_context = dto.context if dto.context and dto.context.get('has_file') else None
        deps = SystemAgentDependencies(
            agent_id=system_agent_id,
            user_id=user_id,
            orion_client=orion_client,
            file_context=file_context
        )
        
        # Enriquece mensagem se houver arquivo anexado
        message_to_send = dto.message
        if file_context:
            file_name = file_context.get('file_name', 'arquivo')
            file_type = file_context.get('file_content_type', '')
            # Adiciona informação sobre o arquivo na mensagem para o agente
            message_to_send = f"{dto.message}\n\n[Arquivo anexado: {file_name} ({file_type})]"
            logger.info(f"📎 Arquivo anexado detectado: {file_name}")
        
        # Executa agente
        try:
            result = system_agent_instance.run_sync(message_to_send, deps=deps)
            execution_time = time.perf_counter() - start_time
            
            # Extrai resposta
            response_text = str(result.data) if hasattr(result, "data") else str(result)
            
            # Extrai ferramentas usadas
            tools_used = []
            if hasattr(result, "tool_calls"):
                tools_used = [call.get("tool_name", "") for call in result.tool_calls]
            
            # Calcula tokens (aproximado)
            tokens_used = len(dto.message.split()) + len(response_text.split())
            
            # Salva execução no MongoDB (assíncrono)
            execution_id = self.system_execution_repository.save_execution(
                system_agent_id=system_agent_id,
                user_id=user_id,
                user_message=dto.message,
                agent_response=response_text,
                tools_used=tools_used,
                execution_metadata={
                    "session_id": dto.session_id,
                    "tokens_used": tokens_used,
                    "execution_time": round(execution_time, 4)
                }
            )
            
            logger.info(f"✅ Agente de sistema executado em {execution_time:.3f}s (tools: {tools_used})")
            
            return {
                "response": response_text,
                "message": dto.message,
                "execution_time": round(execution_time, 4),
                "tokens_used": tokens_used,
                "session_id": dto.session_id,
                "execution_id": execution_id,
                "tools_used": tools_used,
                "system_agent": True
            }
            
        except Exception as exc:
            execution_time = time.perf_counter() - start_time
            logger.error(
                f"❌ Erro ao executar agente de sistema {system_agent_id}: {str(exc)}",
                exc_info=True
            )
            response_text = f"Erro ao processar sua mensagem: {str(exc)}"
            
            return {
                "response": response_text,
                "message": dto.message,
                "execution_time": round(execution_time, 4),
                "tokens_used": 0,
                "session_id": dto.session_id,
                "execution_id": "",
                "tools_used": [],
                "system_agent": True,
                "error": str(exc)
            }
