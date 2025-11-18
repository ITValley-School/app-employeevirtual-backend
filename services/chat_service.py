"""
Service de chat - Orquestrador de casos de uso
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
import logging
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_

from schemas.chat.requests import ChatMessageRequest, ChatSessionRequest
from domain.chat.chat_entity import ChatEntity
from factories.chat_factory import ChatFactory
from data.chat_repository import ChatRepository
from data.chat_mongodb_repository import ChatMongoDBRepository
from data.agent_repository import AgentRepository
from data.entities.chat_entities import ChatSessionEntity, ChatMessageEntity
from services.ai_service import AIService

logger = logging.getLogger(__name__)


def _normalize_model_name(model: str) -> str:
    """
    Normaliza o nome do modelo para uso com Pydantic AI
    Remove prefixos duplicados tipo 'openai:openai:gpt-4o-mini'
    
    Args:
        model: Nome do modelo
        
    Returns:
        str: Modelo normalizado
    """
    if not model:
        return "gpt-4-turbo-preview"
    
    # Remove prefixo 'openai:' se existir (o Pydantic AI já adiciona)
    model = model.strip()
    if model.startswith("openai:"):
        model = model[7:]  # Remove 'openai:'
    
    return model


class ChatService:
    """Service para orquestração de chat"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.chat_mongodb_repository = ChatMongoDBRepository()
        self.agent_repository = AgentRepository(db)
        self.ai_service = AIService()
    
    def create_session(self, dto: ChatSessionRequest, user_id: str) -> ChatEntity:
        """
        Cria nova sessão de chat
        
        Args:
            dto: Dados da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão criada
        """
        # 1. Factory cria Entity a partir do DTO
        session = ChatFactory.create_session(dto, user_id)
        logger.info(f"🏭 Factory criou sessão: ID={session.id}, Title={session.title}, Agent={session.agent_id}")
        
        # 2. Repository persiste Entity no SQL Server
        try:
            persisted = self.chat_repository.add_session(session)
            logger.info(f"✅ Sessão salva no SQL Server: {persisted.id}")
        except Exception as e:
            logger.error(f"❌ ERRO ao salvar no SQL Server: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # 3. Salvar conversa no MongoDB
        try:
            self.chat_mongodb_repository.add_conversation({
                'conversation_id': session.id,
                'user_id': user_id,
                'agent_id': session.agent_id,
                'title': session.title or 'Nova Conversa',
                'context': {}
            })
            logger.info(f"✅ Conversa salva no MongoDB: {session.id}")
        except Exception as e:
            logger.error(f"⚠️ Erro ao salvar conversa no MongoDB: {str(e)}")
            # Não falha a operação se MongoDB cair
        
        return session
    
    def get_session(self, session_id: str, user_id: str) -> Optional[ChatEntity]:
        """
        Busca sessão por ID
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão encontrada ou None
        """
        return self.chat_repository.get_session(session_id, user_id)
    
    def send_message(self, session_id: str, dto: ChatMessageRequest, user_id: str) -> Dict[str, ChatEntity]:
        """
        Envia mensagem para o chat (síncrono)
        
        Args:
            session_id: ID da sessão
            dto: Dados da mensagem
            user_id: ID do usuário
            
        Returns:
            Dict: Dicionário com 'user_message' e 'assistant_response'
        """
        # 1. Busca sessão
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Sessão não encontrada")
        
        # 2. Cria mensagem do usuário via Factory
        user_message = ChatFactory.create_message(dto, session_id, user_id)
        
        # 3. Persiste mensagem do usuário no MongoDB
        self.chat_mongodb_repository.add_message({
            'session_id': session_id,
            'user_id': user_id,
            'agent_id': session.agent_id,
            'message': user_message.message,
            'sender': user_message.sender,
            'context': user_message.context or {},
            'metadata': {
                'message_id': user_message.id,
                'created_at': user_message.created_at
            }
        })
        
        # 4. Busca agente da sessão para obter configurações
        agent = None
        if session.agent_id:
            agent = self.agent_repository.get_agent_by_id(session.agent_id, user_id)
        
        # 6. Gera resposta do agente usando IA
        try:
            # Define configuração padrão do agente
            # Nota: agent.temperature e agent.max_tokens podem ser strings no banco
            agent_config = {
                'name': agent.name if agent else 'Assistente EmployeeVirtual',
                'system_prompt': agent.system_prompt if agent else 'Você é um assistente útil e amigável.',
                'model': _normalize_model_name(agent.model if agent else 'gpt-4-turbo-preview'),
                'temperature': float(agent.temperature or 0.7) if agent else 0.7,
                'max_tokens': int(agent.max_tokens or 2000) if agent else 2000
            }
            
            # Executa IA de forma síncrona usando AIService
            ai_response = self.ai_service.generate_response_sync(
                message=ChatFactory.message_from(dto),
                system_prompt=agent_config['system_prompt'],
                agent_id=session.agent_id,
                user_id=user_id,
                temperature=agent_config['temperature'],
                model=agent_config['model'],
                max_tokens=agent_config['max_tokens']
            )
            
            logger.info(f"✅ Resposta IA gerada para sessão {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com IA: {str(e)}", exc_info=True)
            logger.error(f"   Agent config: {agent_config}")
            logger.error(f"   User message: {ChatFactory.message_from(dto)}")
            # Fallback para resposta padrão
            ai_response = f"Desculpe, houve um erro ao processar sua mensagem. Tente novamente."
        
        # 7. Cria mensagem de resposta do assistente
        assistant_response = ChatFactory.create_message(
            ChatMessageRequest(message=ai_response, context={}),
            session_id,
            user_id
        )
        assistant_response.sender = "assistant"
        
        # 8. Persiste resposta do agente NO MONGODB (não em SQL Server)
        self.chat_mongodb_repository.add_message({
            'session_id': session_id,
            'user_id': user_id,
            'agent_id': session.agent_id,
            'message': assistant_response.message,
            'sender': assistant_response.sender,
            'context': assistant_response.context or {},
            'metadata': {
                'message_id': assistant_response.id,
                'created_at': assistant_response.created_at,
                'agent_config': agent_config if 'agent_config' in locals() else {}
            }
        })
        
        # 9. Retorna ambas as mensagens
        return {
            'user_message': user_message,
            'assistant_response': assistant_response
        }

    async def send_message_async(self, session_id: str, dto: ChatMessageRequest, user_id: str) -> Dict[str, ChatEntity]:
        """
        Envia mensagem para o chat (assíncrono)
        Roda send_message em uma thread separada para evitar 'event loop already running'
        
        Args:
            session_id: ID da sessão
            dto: Dados da mensagem
            user_id: ID do usuário
            
        Returns:
            Dict: Dicionário com 'user_message' e 'assistant_response'
        """
        # Roda método síncrono em thread separada
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.send_message, session_id, dto, user_id)

    
    def get_chat_history(self, session_id: str, user_id: str, page: int = 1, size: int = 20) -> tuple[List[ChatEntity], int]:
        """
        Busca histórico de mensagens do MongoDB
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            page: Página
            size: Tamanho da página
            
        Returns:
            tuple: Lista de mensagens e total
        """
        # Busca do MongoDB (histórico completo)
        mongo_messages = self.chat_mongodb_repository.get_messages_by_session(
            session_id, 
            user_id, 
            limit=1000  # Buscar muitas para fazer paginação
        )
        
        # Aplicar paginação
        total = len(mongo_messages)
        offset = (page - 1) * size
        paginated = mongo_messages[offset:offset + size]
        
        # Converter para ChatEntity
        from domain.chat.chat_entity import ChatEntity
        messages = [
            ChatEntity(
                id=msg.get('id') or msg.get('_id'),
                session_id=msg['session_id'],
                user_id=msg['user_id'],
                message=msg['message'],
                sender=msg['sender'],
                context=msg.get('context', {}),
                created_at=msg['created_at']
            )
            for msg in paginated
        ]
        
        return messages, total
    
    def list_sessions(self, user_id: str, page: int = 1, size: int = 10, status: Optional[str] = None) -> tuple[List[ChatEntity], int]:
        """
        Lista sessões do usuário
        
        Args:
            user_id: ID do usuário
            page: Página
            size: Tamanho da página
            status: Filtro por status
            
        Returns:
            tuple: Lista de sessões e total
        """
        return self.chat_repository.list_sessions(user_id, page, size, status)
    
    def close_session(self, session_id: str, user_id: str) -> ChatEntity:
        """
        Fecha sessão de chat
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
            
        Returns:
            ChatEntity: Sessão fechada
        """
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Sessão não encontrada")
        
        session.close()
        self.chat_repository.update_session(session)
        
        return session
    
    def get_agent_conversations(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Busca todas as conversas ATIVAS de um agente (para sidebar)
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            List: Lista de conversas ativas
        """
        try:
            # Busca conversas do MongoDB
            conversations = self.chat_mongodb_repository.get_agent_conversations(agent_id, user_id)
            
            # Formatar resposta para frontend - APENAS CONVERSAS ATIVAS
            result = []
            for conv in conversations:
                # Filtrar apenas conversas com status 'active'
                status = conv.get('metadata', {}).get('status', 'active')
                if status != 'active':
                    continue
                
                result.append({
                    'id': conv['conversation_id'],
                    'title': conv.get('title', 'Nova Conversa'),
                    'agent_id': agent_id,
                    'user_id': user_id,
                    'last_activity': conv.get('metadata', {}).get('last_activity'),
                    'message_count': conv.get('metadata', {}).get('message_count', 0),
                    'status': status,
                    'created_at': conv.get('metadata', {}).get('created_at')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar conversas do agente: {str(e)}", exc_info=True)
            return []

    def inactivate_conversation_sql(self, session_id: str, user_id: str) -> None:
        """
        Inativa conversa no SQL Server
        
        Args:
            session_id: ID da sessão
            user_id: ID do usuário
        """
        try:
            # Busca a sessão
            session = self.chat_repository.get_session(session_id, user_id)
            if not session:
                raise ValueError(f"Sessão {session_id} não encontrada")
            
            # Muda status para inactive
            session.status = "inactive"
            
            # Persiste no SQL Server
            self.chat_repository.update_session(session)
            logger.info(f"✅ Conversa {session_id} inativada no SQL Server")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inativar conversa no SQL Server: {str(e)}", exc_info=True)
            raise

    def inactivate_conversation_mongo(self, conversation_id: str, user_id: str) -> None:
        """
        Inativa conversa no MongoDB
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário
        """
        try:
            # Inativa conversa no MongoDB
            self.chat_mongodb_repository.inactivate_conversation(conversation_id, user_id)
            logger.info(f"✅ Conversa {conversation_id} inativada no MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inativar conversa no MongoDB: {str(e)}", exc_info=True)
            raise

