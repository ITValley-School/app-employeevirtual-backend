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
from factories.chat_factory import ChatFactory
from mappers.agent_mapper import AgentMapper
from services.ai_service import AIService
from integrations.ai.vector_db_client import VectorDBClient
from integrations.ai.orion_client import OrionClient
from integrations.ai.system_agent_tools import build_system_agent, SystemAgentDependencies
from domain.agents.agent_tools import ToolType
from config.settings import settings

logger = logging.getLogger(__name__)


def _normalize_model_name(model: Optional[str]) -> str:
    """Normaliza nomes de modelos para o formato esperado pelo Pydantic AI"""
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
        self.ai_service = ai_service or AIService.get_instance()
        self.vector_db_client = vector_db_client or VectorDBClient()
        self.agent_document_repository = AgentDocumentRepository()
        self.chat_mongodb_repository = ChatMongoDBRepository()
        self.system_execution_repository = SystemAgentExecutionRepository()
        self.tool_cache_repository = ToolCacheRepository()

    def create_agent(self, dto: AgentCreateRequest, user_id: str) -> AgentEntity:
        """
        Cria novo agente.
        Service apenas orquestra: Factory cria, Repository persiste.
        """
        payload = dto.model_dump()
        payload["user_id"] = user_id

        # Factory cria domain entity (conhece os campos do DTO)
        domain_agent = AgentFactory.create_agent(payload)

        # Repository persiste convertendo internamente via _to_model()
        return self.agent_repository.save(domain_agent)

    def get_agent_by_id(self, agent_id: str, user_id: str) -> Optional[AgentEntity]:
        """Busca agente por ID"""
        return self.agent_repository.get_agent_by_id(agent_id, user_id)

    def get_agent_detail(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """Busca agente com detalhes e estatísticas"""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        stats = self.get_agent_stats(agent_id, user_id)
        return {'agent': agent, 'stats': stats}

    def list_agents(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> Tuple[List[AgentEntity], int]:
        """Lista agentes do usuário"""
        return self.agent_repository.list_agents_by_user(user_id, page, size, status)

    def get_agent_stats(self, agent_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca estatísticas do agente"""
        return None

    def execute_agent(self, agent_id: str, dto: AgentExecuteRequest, user_id: str) -> Dict[str, Any]:
        """
        Executa agente.
        Service orquestra: Factory extrai dados, AI Service gera resposta.
        """
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")

        # Factory extrai dados do DTO (Service não acessa campos)
        message_payload = AgentFactory.build_message_payload(dto)
        message_text = AgentFactory.message_from(dto)
        session_id = AgentFactory.session_id_from(dto)

        # Factory extrai config do agente (Service não acessa campos)
        config = AgentFactory.get_execution_config(agent)
        model = _normalize_model_name(config['model'])

        start_time = time.perf_counter()

        # Verifica se deve usar RAG
        has_docs = self.agent_document_repository.has_documents(config['id'])
        should_use_rag = self.ai_service.supports_rag and has_docs

        try:
            if should_use_rag:
                logger.info(f"🚀 Executando agente {config['id']} ({config['name']}) com RAG")
                response_text = self.ai_service.generate_rag_response_sync(
                    message=message_payload,
                    agent_id=config['id'],
                    agent_name=config['name'],
                    instructions=config['system_prompt']
                )
            else:
                logger.info(f"🚀 Executando agente {config['id']} ({config['name']})")
                response_text = self.ai_service.generate_response_sync(
                    message=message_payload,
                    system_prompt=config['system_prompt'],
                    agent_id=config['id'],
                    user_id=user_id,
                    temperature=config['temperature'],
                    model=model,
                    max_tokens=config['max_tokens']
                )

            if not response_text or len(response_text.strip()) == 0:
                logger.error(f"❌ Resposta vazia do agente {config['id']}")
                response_text = "Desculpe, não consegui gerar uma resposta. Tente novamente."
        except Exception as exc:
            logger.error(f"❌ Erro ao executar agente {config['id']}: {str(exc)}", exc_info=True)
            response_text = f"Erro ao processar sua mensagem: {str(exc)}"

        execution_time = time.perf_counter() - start_time
        logger.info(f"✅ Agente {config['id']} executado em {execution_time:.3f}s")

        tokens_used = AgentFactory.count_tokens(message_text, response_text)

        # Atualiza uso via Factory (Factory conhece os campos)
        AgentFactory.increment_usage(agent)
        self.agent_repository.update_agent(agent)

        # Prepara resultado
        result = {
            'response': response_text,
            'message': message_text,
            'execution_time': round(execution_time, 4),
            'tokens_used': tokens_used,
            'session_id': session_id,
            'rag_used': should_use_rag
        }

        # Salva no MongoDB de forma assíncrona se tiver session_id
        if session_id:
            self._save_conversation_async(
                session_id=session_id,
                user_id=user_id,
                agent_id=config['id'],
                user_message=message_text,
                assistant_message=response_text
            )

        return result

    def _save_conversation_async(self, session_id: str, user_id: str, agent_id: str,
                                  user_message: str, assistant_message: str):
        """Salva conversa no MongoDB de forma assíncrona (não bloqueante)."""
        def save_in_background():
            try:
                # Usa ChatFactory para construir dicts MongoDB
                user_msg = ChatFactory.to_mongo_message_dict(
                    session_id, user_id, agent_id, user_message, 'user'
                )
                self.chat_mongodb_repository.add_message(user_msg)

                asst_msg = ChatFactory.to_mongo_message_dict(
                    session_id, user_id, agent_id, assistant_message, 'assistant'
                )
                self.chat_mongodb_repository.add_message(asst_msg)

                logger.debug(f"✅ Conversa salva no MongoDB (background): {session_id}")
            except Exception as e:
                logger.debug(f"⚠️ Falha ao salvar conversa no MongoDB (não crítico): {str(e)}")

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
        """Envia PDF associado ao agente para serviço vetorial externo."""
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

        # Factory extrai nome do agente para metadados
        agent_name = AgentFactory.name_from_entity(agent)
        metadata.update({
            "agent_id": agent_id,
            "user_id": user_id,
            "agent_name": agent_name,
        })

        metadata_json = json.dumps(metadata)
        final_file_name = file_name or f"{agent_id}.pdf"

        vector_response = self.vector_db_client.upload_pdf(
            file_name=final_file_name,
            content=file_content,
            content_type=content_type,
            namespace=agent_id,
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

    def list_agent_documents(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Lista documentos associados a um agente."""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        return self.agent_document_repository.list_documents(agent_id, user_id)

    def delete_agent_document(self, agent_id: str, document_id: str, user_id: str) -> Dict[str, Any]:
        """Remove documento do agente (MongoDB + Pinecone)."""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")

        document = self.agent_document_repository.get_document_by_id(document_id, user_id)
        if not document:
            raise ValueError("Documento não encontrado")

        if document.get("agent_id") != agent_id:
            raise ValueError("Documento não pertence a este agente")

        file_name = document.get("file_name")
        namespace = agent_id

        vector_delete_result = None
        try:
            if file_name:
                vector_delete_result = self.vector_db_client.delete_document(
                    namespace=namespace, file_name=file_name, delete_all=False
                )
            else:
                logger.warning(f"⚠️ Documento {document_id} não tem file_name, pulando delete no Pinecone")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao deletar documento do Pinecone (continuando com delete do MongoDB): {str(e)}")

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

    def update_agent_document_metadata(self, agent_id: str, document_id: str, user_id: str, metadata_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza metadados de um documento do agente."""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")

        document = self.agent_document_repository.get_document_by_id(document_id, user_id)
        if not document:
            raise ValueError("Documento não encontrado")

        if document.get("agent_id") != agent_id:
            raise ValueError("Documento não pertence a este agente")

        current_metadata = document.get("metadata", {})
        updated_metadata = {**current_metadata, **metadata_updates}

        updated_document = self.agent_document_repository.update_document_metadata(
            document_id=document_id, user_id=user_id, metadata_updates=updated_metadata
        )

        if not updated_document:
            raise ValueError("Erro ao atualizar metadados do documento")

        return {"success": True, "document": updated_document}

    def build_execute_request_from_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: Optional[str],
        message: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AgentExecuteRequest:
        """Constrói AgentExecuteRequest a partir de arquivo recebido via multipart."""
        import base64

        if not message:
            content_type_lower = (content_type or "").lower()
            if content_type_lower.startswith('audio/'):
                message = "Transcreva este áudio"
            elif content_type_lower.startswith('video/'):
                message = "Transcreva este vídeo"
            elif content_type_lower.startswith('image/'):
                message = "Extraia o texto desta imagem"
            elif content_type_lower == 'application/pdf':
                message = "Processe este PDF"
            else:
                message = "Processe este arquivo"

        file_base64 = base64.b64encode(file_content).decode('utf-8')

        return AgentExecuteRequest(
            message=message,
            session_id=session_id,
            context={
                "file_content_base64": file_base64,
                "file_name": file_name,
                "file_content_type": content_type,
                "file_size": len(file_content),
                "has_file": True
            }
        )

    def activate_agent(self, agent_id: str, user_id: str) -> AgentEntity:
        """Ativa agente"""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        agent.activate()
        self.agent_repository.update_agent(agent)
        return agent

    def deactivate_agent(self, agent_id: str, user_id: str) -> AgentEntity:
        """Desativa agente"""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        agent.deactivate()
        self.agent_repository.update_agent(agent)
        return agent

    def start_training(self, agent_id: str, user_id: str) -> AgentEntity:
        """Inicia treinamento do agente"""
        agent = self.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        agent.start_training()
        self.agent_repository.update_agent(agent)
        return agent

    # ========== MÉTODOS PARA AGENTES DE SISTEMA ==========

    def get_system_agents(self) -> List[SystemAgentEntity]:
        """Lista todos os agentes de sistema ativos"""
        return self.system_agent_repository.list_all()

    def get_system_agent_by_id(self, agent_id: str) -> Optional[SystemAgentEntity]:
        """Busca agente de sistema por ID"""
        return self.system_agent_repository.get_by_id(agent_id)

    def get_system_agents_by_type(self, agent_type: str) -> List[SystemAgentEntity]:
        """Lista agentes de sistema por tipo"""
        return self.system_agent_repository.get_by_type(agent_type)

    def _get_tools_for_system_agent(self, system_agent: SystemAgentEntity) -> List[str]:
        """Determina ferramentas disponíveis baseado no tipo do agente"""
        tools_mapping = {
            "transcriber": [ToolType.TRANSCRIBE_AUDIO, ToolType.TRANSCRIBE_YOUTUBE],
            "ocr": [ToolType.OCR_IMAGE],
            "document_processor": [ToolType.PROCESS_PDF, ToolType.EXTRACT_TEXT],
            "assistant": [ToolType.TRANSCRIBE_AUDIO, ToolType.OCR_IMAGE, ToolType.PROCESS_PDF],
        }
        # Factory extrai tipo do agente de sistema
        agent_type = AgentFactory.get_system_agent_type(system_agent)
        return tools_mapping.get(agent_type, [])

    def execute_system_agent(self, system_agent_id: str, dto: AgentExecuteRequest, user_id: str) -> Dict[str, Any]:
        """Executa agente de sistema com ferramentas avançadas"""
        start_time = time.perf_counter()

        system_agent = self.get_system_agent_by_id(system_agent_id)
        if not system_agent:
            raise ValueError("Agente de sistema não encontrado ou inativo")

        # Factory extrai dados do DTO e da entidade
        sys_config = AgentFactory.get_system_agent_config(system_agent)
        message_text = AgentFactory.message_from(dto)
        session_id = AgentFactory.session_id_from(dto)
        file_context = AgentFactory.has_file_context(dto)

        logger.info(f"🚀 Executando agente de sistema: {sys_config['name']} ({system_agent_id})")

        # Determina ferramentas habilitadas
        enabled_tools = self._get_tools_for_system_agent(system_agent)
        logger.info(f"🔧 Ferramentas habilitadas: {enabled_tools}")

        # Cria cliente Orion
        orion_client = None
        if enabled_tools:
            orion_url = sys_config.get('orion_endpoint') or settings.orion_api_url
            if orion_url:
                try:
                    orion_client = OrionClient(base_url=orion_url)
                    logger.info(f"✅ Cliente Orion inicializado: {orion_url}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao inicializar Orion: {e}")
            else:
                logger.warning("⚠️ Orion não configurado.")

        # Constrói agente com ferramentas
        system_agent_instance = build_system_agent(
            system_prompt=sys_config['system_prompt'],
            enabled_tools=enabled_tools,
            orion_client=orion_client
        )

        # Prepara dependências
        deps = SystemAgentDependencies(
            agent_id=system_agent_id,
            user_id=user_id,
            orion_client=orion_client,
            file_context=file_context
        )

        # Enriquece mensagem com info de arquivo via Factory
        message_to_send = AgentFactory.build_enriched_message(dto, system_agent)

        # Executa agente
        try:
            result = system_agent_instance.run_sync(message_to_send, deps=deps)
            execution_time = time.perf_counter() - start_time

            response_text = str(result.data) if hasattr(result, "data") else str(result)

            tools_used = []
            if hasattr(result, "tool_calls"):
                tools_used = [call.get("tool_name", "") for call in result.tool_calls]

            tokens_used = AgentFactory.count_tokens(message_text, response_text)

            # Salva execução no MongoDB
            execution_id = self.system_execution_repository.save_execution(
                system_agent_id=system_agent_id,
                user_id=user_id,
                user_message=message_text,
                agent_response=response_text,
                tools_used=tools_used,
                execution_metadata={
                    "session_id": session_id,
                    "tokens_used": tokens_used,
                    "execution_time": round(execution_time, 4)
                }
            )

            logger.info(f"✅ Agente de sistema executado em {execution_time:.3f}s (tools: {tools_used})")

            return {
                "response": response_text,
                "message": message_text,
                "execution_time": round(execution_time, 4),
                "tokens_used": tokens_used,
                "session_id": session_id,
                "execution_id": execution_id,
                "tools_used": tools_used,
                "system_agent": True
            }

        except Exception as exc:
            execution_time = time.perf_counter() - start_time
            logger.error(f"❌ Erro ao executar agente de sistema {system_agent_id}: {str(exc)}", exc_info=True)

            return {
                "response": f"Erro ao processar sua mensagem: {str(exc)}",
                "message": message_text,
                "execution_time": round(execution_time, 4),
                "tokens_used": 0,
                "session_id": session_id,
                "execution_id": "",
                "tools_used": [],
                "system_agent": True,
                "error": str(exc)
            }
