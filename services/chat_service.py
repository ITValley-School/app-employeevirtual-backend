"""
Service de chat - Orquestrador de casos de uso
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
import logging
import asyncio
from sqlalchemy.orm import Session

from schemas.chat.requests import ChatMessageRequest, ChatSessionRequest
from domain.chat.chat_entity import ChatEntity
from factories.chat_factory import ChatFactory
from factories.agent_factory import AgentFactory
from data.chat_repository import ChatRepository
from data.chat_mongodb_repository import ChatMongoDBRepository
from data.agent_repository import AgentRepository
from data.agent_document_repository import AgentDocumentRepository
from data.entities.chat_entities import ChatSessionEntity, ChatMessageEntity
from services.ai_service import AIService

logger = logging.getLogger(__name__)


def _normalize_model_name(model: str) -> str:
    """Normaliza o nome do modelo para uso com Pydantic AI"""
    if not model:
        return "gpt-4-turbo-preview"
    model = model.strip()
    if model.startswith("openai:"):
        model = model[7:]
    return model


class ChatService:
    """Service para orquestração de chat"""

    def __init__(self, db: Session):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.chat_mongodb_repository = ChatMongoDBRepository()
        self.agent_repository = AgentRepository(db)
        self.ai_service = AIService.get_instance()

    def create_session(self, dto: ChatSessionRequest, user_id: str) -> ChatEntity:
        """
        Cria nova sessão de chat ou retorna sessão existente ativa.
        Service orquestra: Factory cria, Repository persiste.
        """
        # 1. Verifica se já existe sessão ativa via Factory helper
        agent_id = ChatFactory.agent_id_from(dto)
        if agent_id:
            existing_session = self.chat_repository.get_active_session_by_agent(
                agent_id=agent_id,
                user_id=user_id
            )
            if existing_session:
                logger.info(f"♻️ Reutilizando sessão existente para agent={agent_id}, user={user_id}")
                return existing_session

        # 2. Factory cria sessão (conhece campos do DTO)
        session = ChatFactory.create_session(dto, user_id)
        session_id = ChatFactory.id_from(session)
        logger.info(f"🏭 Factory criou sessão: ID={session_id}")

        # 3. Repository persiste no SQL Server
        try:
            persisted = self.chat_repository.add_session(session)
            logger.info(f"✅ Sessão salva no SQL Server: {ChatFactory.id_from(persisted)}")
        except Exception as e:
            logger.error(f"❌ ERRO ao salvar no SQL Server: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        # 4. Salvar conversa no MongoDB via Factory helper
        try:
            mongo_conv = ChatFactory.to_mongo_conversation(session, user_id)
            self.chat_mongodb_repository.add_conversation(mongo_conv)
            logger.info(f"✅ Conversa salva no MongoDB: {session_id}")
        except Exception as e:
            logger.error(f"⚠️ Erro ao salvar conversa no MongoDB: {str(e)}")

        return session

    def get_session(self, session_id: str, user_id: str) -> Optional[ChatEntity]:
        """Busca sessão por ID"""
        return self.chat_repository.get_session(session_id, user_id)

    def send_message(self, session_id: str, dto: ChatMessageRequest, user_id: str) -> Dict[str, ChatEntity]:
        """
        Envia mensagem para o chat (síncrono).
        Service orquestra: Factory cria, Repository persiste, AI Service gera resposta.
        """
        # 1. Busca sessão
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Sessão não encontrada")

        # 2. Factory cria mensagem do usuário (conhece campos do DTO)
        user_message = ChatFactory.create_message(dto, session_id, user_id)

        # 3. Persiste no MongoDB via Factory helper
        agent_id = ChatFactory.agent_id_from_session(session)
        mongo_user_msg = ChatFactory.to_mongo_message(user_message, session_id, user_id, agent_id or '')
        self.chat_mongodb_repository.add_message(mongo_user_msg)

        # 4. Busca agente da sessão para obter configurações
        agent = None
        if agent_id:
            agent = self.agent_repository.get_agent_by_id(agent_id, user_id)

        # 5. Factory extrai config do agente (Service não acessa campos)
        agent_config = AgentFactory.get_execution_config(agent) if agent else AgentFactory.get_default_execution_config()

        # 6. Gera resposta do agente usando IA
        try:
            has_docs = False
            should_use_rag = False
            if agent_id:
                doc_repo = AgentDocumentRepository()
                has_docs = doc_repo.has_documents(agent_id)
                should_use_rag = self.ai_service.supports_rag and has_docs

            # Factory extrai mensagem do DTO
            message_text = ChatFactory.message_from(dto)

            if should_use_rag and agent:
                logger.info(f"🔎 Usando RAG para agente {agent_id}")
                ai_response = self.ai_service.generate_rag_response_sync(
                    message=message_text,
                    agent_id=agent_config['id'],
                    agent_name=agent_config['name'],
                    instructions=agent_config['system_prompt']
                )
            else:
                ai_response = self.ai_service.generate_response_sync(
                    message=message_text,
                    system_prompt=agent_config['system_prompt'],
                    agent_id=agent_config['id'],
                    user_id=user_id,
                    temperature=agent_config['temperature'],
                    model=_normalize_model_name(agent_config['model']),
                    max_tokens=agent_config['max_tokens']
                )

            logger.info(f"✅ Resposta IA gerada para sessão {session_id}")

        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com IA: {str(e)}", exc_info=True)
            ai_response = "Desculpe, houve um erro ao processar sua mensagem. Tente novamente."

        # 7. Factory cria mensagem de resposta do assistente
        assistant_response = ChatFactory.create_assistant_message(ai_response, session_id, user_id)

        # 8. Persiste resposta no MongoDB via Factory helper
        mongo_asst_msg = ChatFactory.to_mongo_message(
            assistant_response, session_id, user_id, agent_id or '',
            extra_metadata={'agent_config': agent_config}
        )
        self.chat_mongodb_repository.add_message(mongo_asst_msg)

        # 9. Retorna ambas as mensagens
        return {
            'user_message': user_message,
            'assistant_response': assistant_response
        }

    async def send_message_async(self, session_id: str, dto: ChatMessageRequest, user_id: str) -> Dict[str, ChatEntity]:
        """Envia mensagem para o chat (assíncrono)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.send_message, session_id, dto, user_id)

    def get_chat_history(self, session_id: str, user_id: str, page: int = 1, size: int = 20) -> tuple[List[ChatEntity], int]:
        """Busca histórico de mensagens do MongoDB"""
        # Busca do MongoDB
        mongo_messages = self.chat_mongodb_repository.get_messages_by_session(
            session_id, user_id, limit=1000
        )

        # Paginação
        total = len(mongo_messages)
        offset = (page - 1) * size
        paginated = mongo_messages[offset:offset + size]

        # Factory converte dicts do MongoDB para ChatEntity
        messages = [ChatFactory.from_mongo_message(msg) for msg in paginated]

        return messages, total

    def list_sessions(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> tuple[List[ChatEntity], int]:
        """Lista sessões do usuário"""
        return self.chat_repository.list_sessions(user_id, page, size, status)

    def close_session(self, session_id: str, user_id: str) -> ChatEntity:
        """Fecha sessão de chat"""
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Sessão não encontrada")

        # Método de domínio (permitido pela Regra 5)
        session.close()
        self.chat_repository.update_session(session)

        return session

    def get_agent_conversations(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Busca todas as conversas ATIVAS de um agente (para sidebar)"""
        try:
            conversations = self.chat_mongodb_repository.get_agent_conversations(agent_id, user_id)

            # Factory converte e filtra conversas ativas
            result = []
            for conv in conversations:
                sidebar_item = ChatFactory.from_mongo_conversation(conv, agent_id, user_id)
                if sidebar_item['status'] == 'active':
                    result.append(sidebar_item)

            return result

        except Exception as e:
            logger.error(f"Erro ao buscar conversas do agente: {str(e)}", exc_info=True)
            return []

    def inactivate_conversation_sql(self, session_id: str, user_id: str) -> None:
        """Inativa conversa no SQL Server"""
        try:
            session = self.chat_repository.get_session(session_id, user_id)
            if not session:
                raise ValueError(f"Sessão {session_id} não encontrada")

            # Método de domínio para fechar/inativar
            session.close()
            self.chat_repository.update_session(session)
            logger.info(f"✅ Conversa {session_id} inativada no SQL Server")

        except Exception as e:
            logger.error(f"❌ Erro ao inativar conversa no SQL Server: {str(e)}", exc_info=True)
            raise

    def inactivate_conversation_mongo(self, conversation_id: str, user_id: str) -> None:
        """Inativa conversa no MongoDB"""
        try:
            self.chat_mongodb_repository.inactivate_conversation(conversation_id, user_id)
            logger.info(f"✅ Conversa {conversation_id} inativada no MongoDB")
        except Exception as e:
            logger.error(f"❌ Erro ao inativar conversa no MongoDB: {str(e)}", exc_info=True)
            raise
