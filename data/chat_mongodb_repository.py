"""
Repository para Chat no MongoDB
Persistência em um único documento chat_conversations com todas as mensagens
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from data.mongodb import get_database, Collections

logger = logging.getLogger(__name__)


class ChatMongoDBRepository:
    """Repository para persistência de chat no MongoDB"""
    
    def __init__(self):
        self.db = get_database()
    
    def add_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """
        Adiciona conversa no MongoDB
        
        Args:
            conversation_data: Dados da conversa
            
        Returns:
            str: ID da conversa criada
        """
        try:
            conversation_doc = {
                '_id': conversation_data['conversation_id'],
                'conversation_id': conversation_data['conversation_id'],
                'user_id': conversation_data['user_id'],
                'agent_id': conversation_data.get('agent_id'),
                'title': conversation_data.get('title', 'Nova Conversa'),
                'messages': [],  # Todas as mensagens aqui
                'context': conversation_data.get('context', {}),
                'metadata': {
                    'created_at': datetime.utcnow(),
                    'last_activity': datetime.utcnow(),
                    'message_count': 0,
                    'status': 'active',
                    'total_tokens': 0,
                    'total_cost': 0.0
                }
            }
            
            result = self.db[Collections.CHAT_CONVERSATIONS].insert_one(conversation_doc)
            logger.info(f"✅ Conversa salva no MongoDB: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            error_msg = str(e)
            is_timeout = (
                'timeout' in error_msg.lower() or 
                'timed out' in error_msg.lower() or
                'ServerSelectionTimeoutError' in type(e).__name__
            )
            if is_timeout:
                logger.warning(
                    f"⏱️ Timeout ao salvar conversa no MongoDB. "
                    f"Conversa foi salva no SQL Server. Continuando sem MongoDB."
                )
                # Retorna ID da conversa mesmo sem MongoDB (já foi salva no SQL)
                return conversation_doc.get('conversation_id', conversation_doc.get('_id', ''))
            logger.error(f"❌ Erro ao salvar conversa no MongoDB: {error_msg}", exc_info=True)
            # Não levanta exceção - permite que o sistema continue
            return conversation_doc.get('conversation_id', conversation_doc.get('_id', ''))
    
    def add_message(self, message_data: Dict[str, Any]) -> str:
        """
        Adiciona mensagem dentro de uma conversa no MongoDB
        
        Args:
            message_data: Dados da mensagem {
                'session_id': str,
                'user_id': str,
                'agent_id': str,
                'message': str,
                'sender': str ('user' ou 'assistant'),
                'context': dict,
                'metadata': dict
            }
            
        Returns:
            str: ID da mensagem criada
        """
        try:
            # Preparar documento de mensagem
            message_doc = {
                '_id': ObjectId(),  # ID único da mensagem
                'message': message_data['message'],
                'sender': message_data['sender'],
                'context': message_data.get('context', {}),
                'metadata': message_data.get('metadata', {}),
                'created_at': datetime.utcnow()
            }
            
            # Adicionar mensagem ao array de mensagens da conversa
            result = self.db[Collections.CHAT_CONVERSATIONS].update_one(
                {'_id': message_data['session_id']},
                {
                    '$push': {'messages': message_doc},
                    '$inc': {'metadata.message_count': 1},
                    '$set': {'metadata.last_activity': datetime.utcnow()}
                }
            )
            
            if result.modified_count == 0:
                logger.warning(f"⚠️ Conversa {message_data['session_id']} não encontrada no MongoDB")
                # Não levanta exceção - permite que o sistema continue
                return str(message_doc['_id'])
            
            logger.info(f"✅ Mensagem adicionada à conversa: {message_data['session_id']}")
            return str(message_doc['_id'])
            
        except Exception as e:
            error_msg = str(e)
            is_timeout = (
                'timeout' in error_msg.lower() or 
                'timed out' in error_msg.lower() or
                'ServerSelectionTimeoutError' in type(e).__name__
            )
            if is_timeout:
                logger.warning(
                    f"⏱️ Timeout ao adicionar mensagem no MongoDB. "
                    f"Mensagem processada mas não salva no MongoDB."
                )
            else:
                logger.error(f"❌ Erro ao adicionar mensagem: {error_msg}", exc_info=True)
            # Não levanta exceção - permite que o sistema continue
            return str(message_doc.get('_id', ''))
    
    def get_user_conversations(self, user_id: str, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca conversas de um usuário
        
        Args:
            user_id: ID do usuário
            agent_id: ID do agente (opcional)
            
        Returns:
            List: Lista de conversas
        """
        try:
            query = {'user_id': user_id}
            if agent_id:
                query['agent_id'] = agent_id
            
            conversations = list(
                self.db[Collections.CHAT_CONVERSATIONS]
                .find(query)
                .sort('metadata.last_activity', -1)
                .limit(100)
            )
            
            for conv in conversations:
                conv['_id'] = str(conv['_id'])
                conv['id'] = conv['conversation_id']
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar conversas: {str(e)}", exc_info=True)
            return []
    
    def get_agent_conversations(self, agent_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca conversas de um agente (para sidebar)
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário (opcional)
            
        Returns:
            List: Lista de conversas
        """
        try:
            query = {'agent_id': agent_id}
            if user_id:
                query['user_id'] = user_id
            
            # Adiciona timeout específico para a query (5s)
            # Cria cursor e aplica timeout
            collection = self.db[Collections.CHAT_CONVERSATIONS]
            cursor = collection.find(query).max_time_ms(5000)  # Timeout de 5s
            conversations = list(
                cursor
                .sort('metadata.last_activity', -1)
                .limit(100)
            )
            
            for conv in conversations:
                conv['_id'] = str(conv['_id'])
                conv['id'] = conv['conversation_id']
            
            logger.debug(f"✅ {len(conversations)} conversas encontradas para agente {agent_id}")
            return conversations
            
        except Exception as e:
            error_msg = str(e)
            # Tratamento específico para timeouts
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                logger.warning(
                    f"⏱️ Timeout ao buscar conversas do agente {agent_id}. "
                    f"MongoDB pode estar lento ou indisponível. Retornando lista vazia."
                )
            else:
                logger.error(
                    f"❌ Erro ao buscar conversas do agente {agent_id}: {error_msg}",
                    exc_info=True
                )
            # Retorna lista vazia em caso de erro (não quebra o fluxo)
            return []
    
    def get_messages_by_session(self, session_id: str, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca mensagens de uma conversa
        
        Args:
            session_id: ID da sessão/conversa
            user_id: ID do usuário
            limit: Limite de mensagens
            
        Returns:
            List: Lista de mensagens
        """
        try:
            conversation = self.db[Collections.CHAT_CONVERSATIONS].find_one(
                {'_id': session_id, 'user_id': user_id},
                {'messages': {'$slice': -limit}}  # Últimas N mensagens
            )
            
            if not conversation:
                logger.warning(f"⚠️ Conversa não encontrada: {session_id}")
                return []
            
            messages = conversation.get('messages', [])
            
            # Converter ObjectId para string e garantir dados completos
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    '_id': str(msg.get('_id', '')),
                    'id': str(msg.get('_id', '')),
                    'message': msg.get('message', ''),
                    'sender': msg.get('sender', ''),
                    'context': msg.get('context', {}),
                    'metadata': msg.get('metadata', {}),
                    'created_at': msg.get('created_at'),
                    'session_id': session_id,
                    'user_id': user_id
                }
                formatted_messages.append(formatted_msg)
            
            logger.info(f"✅ {len(formatted_messages)} mensagens recuperadas da conversa {session_id}")
            return formatted_messages
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar mensagens: {str(e)}", exc_info=True)
            return []
    
    def get_conversation_with_messages(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca conversa completa com todas as mensagens
        
        Args:
            session_id: ID da conversa
            user_id: ID do usuário
            
        Returns:
            Dict: Conversa com todas as mensagens ou None
        """
        try:
            conversation = self.db[Collections.CHAT_CONVERSATIONS].find_one(
                {'_id': session_id, 'user_id': user_id}
            )
            
            if not conversation:
                return None
            
            conversation['_id'] = str(conversation['_id'])
            conversation['id'] = conversation['conversation_id']
            
            # Converter ObjectId das mensagens para string
            for msg in conversation.get('messages', []):
                if '_id' in msg:
                    msg['_id'] = str(msg['_id'])
                    msg['id'] = str(msg['_id'])
            
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar conversa: {str(e)}", exc_info=True)
            return None
    
    def create_indexes(self):
        """
        Cria índices otimizados
        """
        try:
            # Índice para buscar conversas de um usuário
            self.db[Collections.CHAT_CONVERSATIONS].create_index([
                ('user_id', 1),
                ('metadata.last_activity', -1)
            ])
            
            # Índice para buscar conversas de um agente
            self.db[Collections.CHAT_CONVERSATIONS].create_index([
                ('agent_id', 1),
                ('metadata.last_activity', -1)
            ])
            
            # Índice para buscar por status
            self.db[Collections.CHAT_CONVERSATIONS].create_index([
                ('metadata.status', 1),
                ('metadata.last_activity', -1)
            ])
            
            logger.info("✅ Índices MongoDB criados com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar índices: {str(e)}", exc_info=True)

    def inactivate_conversation(self, conversation_id: str, user_id: str) -> None:
        """
        Inativa conversa no MongoDB
        
        Args:
            conversation_id: ID da conversa (pode ser _id, id ou session_id)
            user_id: ID do usuário
        """
        try:
            # Tentar buscar por múltiplos campos
            query = {
                'user_id': user_id,
                '$or': [
                    {'id': conversation_id},
                    {'session_id': conversation_id},
                    {'_id': conversation_id}  # Tentar como string primeiro
                ]
            }
            
            # Se for um ObjectId válido, tentar também como ObjectId
            try:
                from bson import ObjectId
                query['$or'].append({'_id': ObjectId(conversation_id)})
            except:
                pass
            
            result = self.db[Collections.CHAT_CONVERSATIONS].update_one(
                query,
                {
                    '$set': {
                        'metadata.status': 'inactive'
                    }
                }
            )
            
            if result.matched_count == 0:
                logger.warning(f"Conversa {conversation_id} nao encontrada ou nao pertence ao usuario")
                raise ValueError(f"Conversa {conversation_id} nao encontrada")
            
            logger.info(f"Conversa {conversation_id} inativada no MongoDB")
            
        except Exception as e:
            logger.error(f"Erro ao inativar conversa no MongoDB: {str(e)}", exc_info=True)
            raise

