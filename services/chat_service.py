"""
Serviço de chat/conversação para o sistema EmployeeVirtual - Nova implementação
Usa arquitetura híbrida: SQL Server (metadados) + MongoDB (histórico de chat)
"""
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from data.chat_repository import ChatRepository
from data.agent_repository import AgentRepository
from data.user_repository import UserRepository
from data.mongodb import (
    create_chat_conversation, add_messages_to_conversation, 
    get_conversation_history, update_conversation_context,
    get_user_conversations, update_conversation_metadata,
    delete_conversation, get_conversation_analytics
)
from models.chat_models import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse, ChatRequest, ChatResponse,
    ConversationWithMessages, ConversationSummary, MessageType, ConversationStatus
)
from pydantic_ai import Agent as PydanticAgent


class ChatService:
    """Serviço para gerenciamento de chat/conversação - Nova implementação"""
    
    def __init__(self, db: Session):
        self.chat_repository = ChatRepository(db)
        self.agent_repository = AgentRepository(db)
        self.user_repository = UserRepository(db)
        # Pydantic AI será inicializado por agente
    
    async def create_conversation(self, user_id: str, conversation_data: ConversationCreate) -> ConversationResponse:
        """
        Cria uma nova conversação usando arquitetura híbrida
        
        Args:
            user_id: ID do usuário
            conversation_data: Dados da conversação
            
        Returns:
            ConversationResponse: Dados da conversação criada
        """
        # Verificar se agente existe e pertence ao usuário
        agent = self.agent_repository.get_agent_by_id(conversation_data.agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Criar conversação no SQL Server (metadados)
        conversation = self.chat_repository.create_conversation(
            user_id=user_id,
            agent_id=conversation_data.agent_id,
            title=conversation_data.title or f"Conversa com {agent.name}"
        )
        
        # Criar documento no MongoDB (histórico de chat)
        mongo_data = {
            "conversation_id": str(conversation.id),
            "user_id": user_id,
            "agent_id": str(conversation_data.agent_id),
            "title": conversation.title,
            "context": conversation_data.context or {}
        }
        
        await create_chat_conversation(mongo_data)
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="conversation_created",
            description=f"Nova conversa iniciada com agente '{agent.name}'"
        )
        
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            agent_name=agent.name,
            title=conversation.title,
            status=conversation.status,
            message_count=0,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at
        )
    
    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[ConversationResponse]:
        """
        Busca conversações do usuário usando MongoDB
        
        Args:
            user_id: ID do usuário
            limit: Limite de conversações
            
        Returns:
            Lista de resumos de conversações
        """
        # Buscar conversas do MongoDB
        mongo_conversations = await get_user_conversations(user_id, limit)
        
        result = []
        for conv in mongo_conversations:
            # Buscar nome do agente do SQL Server
            agent = self.agent_repository.get_agent_by_id(conv['agent_id'])
            agent_name = agent.name if agent else "Agente não encontrado"
            
            # Extrair message_count corretamente
            message_count = conv.get('message_count', 0)
            if isinstance(message_count, dict):
                # Se for um objeto MongoDB, usar valor padrão
                message_count = 0
            
            result.append(ConversationResponse(
                id=conv['conversation_id'],
                user_id=user_id,
                agent_id=conv['agent_id'],
                title=conv['title'],
                agent_name=agent_name,
                status=ConversationStatus.ACTIVE,  # Assumir ativo por padrão
                message_count=message_count,
                created_at=conv['last_activity'],
                updated_at=conv['last_activity'],
                last_message_at=conv['last_activity']
            ))
        
        return result
    
    async def get_conversation_with_messages(self, conversation_id: str, user_id: str, 
                                     message_limit: int = 50) -> Optional[ConversationWithMessages]:
        """
        Busca conversação com suas mensagens usando MongoDB
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            message_limit: Limite de mensagens
            
        Returns:
            ConversationWithMessages ou None se não encontrada
        """
        # Buscar histórico do MongoDB
        mongo_data = await get_conversation_history(conversation_id, message_limit)
        if not mongo_data:
            return None
        
        # Buscar metadados do SQL Server
        conversation = self.chat_repository.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        
        # Buscar nome do agente
        agent = self.agent_repository.get_agent_by_id(conversation.agent_id)
        agent_name = agent.name if agent else "Agente não encontrado"
        
        # Converter mensagens do MongoDB
        message_responses = []
        for msg in mongo_data.get("messages", []):
            # Garantir que user_id sempre tenha um valor válido
            msg_user_id = msg.get("user_id") or user_id
            if not msg_user_id:
                msg_user_id = str(uuid.uuid4())  # Fallback se ainda for None
            
            message_responses.append(MessageResponse(
                id=msg.get("id", str(uuid.uuid4())),
                conversation_id=conversation_id,
                user_id=msg_user_id,
                content=msg["content"],
                message_type=msg["message_type"],
                agent_id=msg.get("agent_id") if msg["message_type"] == "agent" else None,
                metadata=msg.get("metadata", {}),
                created_at=msg.get("timestamp", datetime.utcnow())
            ))
        
        return ConversationWithMessages(
            id=conversation.id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            agent_name=agent_name,
            title=conversation.title,
            status=conversation.status,
            messages=message_responses,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at
        )
    
    async def send_message(self, user_id: str, message_data: MessageCreate) -> MessageResponse:
        """
        Envia uma mensagem em uma conversação usando MongoDB
        
        Args:
            user_id: ID do usuário
            message_data: Dados da mensagem
            
        Returns:
            MessageResponse: Mensagem criada
        """
        # Verificar se conversação existe e pertence ao usuário
        conversation = self.chat_repository.get_conversation_by_id(message_data.conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversação não encontrada")
        
        # Criar mensagem do usuário no MongoDB
        message_id = str(uuid.uuid4())
        user_message_data = {
            "id": message_id,
            "content": message_data.content,
            "message_type": "user",
            "user_id": user_id,
            "metadata": message_data.message_metadata or {}
        }
        
        # Salvar mensagem no MongoDB
        success = await add_messages_to_conversation(
            str(message_data.conversation_id), 
            [user_message_data]
        )
        
        if not success:
            raise ValueError("Erro ao salvar mensagem no MongoDB")
        
        # Atualizar metadados no SQL Server
        self.chat_repository.update_conversation(
            message_data.conversation_id,
            user_id,
            last_message_at=datetime.utcnow()
        )
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="message_sent",
            description=f"Mensagem enviada na conversa '{conversation.title}'"
        )
        
        return MessageResponse(
            id=message_id,
            conversation_id=message_data.conversation_id,
            user_id=user_id,
            content=message_data.content,
            message_type=MessageType.USER,
            agent_id=None,
            metadata=message_data.metadata,
            created_at=datetime.utcnow()
        )
    
    async def process_chat_request(self, user_id: str, chat_request: ChatRequest) -> ChatResponse:
        """
        Processa uma requisição de chat completa usando MongoDB
        
        Args:
            user_id: ID do usuário
            chat_request: Dados da requisição
            
        Returns:
            ChatResponse: Resposta do chat
        """
        try:
            # Buscar conversação
            conversation = self.chat_repository.get_conversation_by_id(chat_request.conversation_id, user_id)
            if not conversation:
                raise ValueError("Conversação não encontrada")
            
            # Buscar agente
            agent = self.agent_repository.get_agent_by_id(conversation.agent_id, user_id)
            if not agent:
                raise ValueError("Agente não encontrado")
            
            # Buscar histórico de mensagens do MongoDB para contexto
            mongo_data = await get_conversation_history(str(chat_request.conversation_id), 20)
            recent_messages = mongo_data.get("messages", []) if mongo_data else []
            
            # Preparar contexto para o agente
            context_messages = []
            for msg in recent_messages[-10:]:  # Últimas 10 mensagens
                role = "user" if msg.get("message_type") == "user" else "assistant"
                context_messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })
            
            # Adicionar mensagem atual
            context_messages.append({
                "role": "user",
                "content": chat_request.message
            })
            
            # Criar agente Pydantic AI com as configurações do agente
            pydantic_agent = PydanticAgent(
                model=agent.model,
                system_prompt=agent.system_prompt
            )
            
            # Processar mensagem com o agente
            try:
                # Usar apenas a mensagem atual para simplificar
                result = await pydantic_agent.run(chat_request.message)
                response_content = result.data
                
                orion_response = {
                    "status": "success",
                    "response": response_content,
                    "metadata": {
                        "model_used": agent.model,
                        "tokens_used": len(chat_request.message) + len(response_content),
                        "execution_time": 1.0,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                
            except Exception as e:
                # Log do erro para debug
                print(f"❌ Erro no Pydantic AI: {str(e)}")
                orion_response = {
                    "status": "error",
                    "error_message": f"Erro ao processar com agente: {str(e)}"
                }
            
            # Preparar mensagens para salvar no MongoDB
            user_message_id = str(uuid.uuid4())
            agent_message_id = str(uuid.uuid4())
            
            messages_to_save = [
                {
                    "id": user_message_id,
                    "content": chat_request.message,
                    "message_type": "user",
                    "user_id": user_id,
                    "metadata": {
                        "timestamp": datetime.utcnow()
                    }
                },
                {
                    "id": agent_message_id,
                    "content": orion_response.get('response', 'Erro ao processar resposta'),
                    "message_type": "agent",
                    "agent_id": str(agent.id),
                    "metadata": {
                        "processing_time": orion_response.get('processing_time', 0),
                        "model_used": orion_response.get('model_used', ''),
                        "tokens_used": orion_response.get('tokens_used', 0),
                        "timestamp": datetime.utcnow()
                    }
                }
            ]
            
            # Salvar mensagens no MongoDB (atômico)
            success = await add_messages_to_conversation(
                str(chat_request.conversation_id), 
                messages_to_save
            )
            
            if not success:
                raise ValueError("Erro ao salvar mensagens no MongoDB")
            
            # Atualizar metadados no SQL Server
            self.chat_repository.update_conversation(
                chat_request.conversation_id,
                user_id,
                last_message_at=datetime.utcnow()
            )
            
            # Atualizar metadados no MongoDB
            await update_conversation_metadata(
                str(chat_request.conversation_id),
                {
                    "total_tokens": orion_response.get('tokens_used', 0),
                    "total_cost": orion_response.get('cost', 0.0)
                }
            )
            
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="chat_processed",
                description=f"Chat processado com agente '{agent.name}'"
            )
            
            return ChatResponse(
                conversation_id=chat_request.conversation_id,
                user_message=MessageResponse(
                    id=user_message_id,
                    conversation_id=chat_request.conversation_id,
                    user_id=user_id,
                    content=chat_request.message,
                    message_type=MessageType.USER,
                    agent_id=None,
                    metadata={"timestamp": datetime.utcnow()},
                    created_at=datetime.utcnow()
                ),
                agent_response=MessageResponse(
                    id=agent_message_id,
                    conversation_id=chat_request.conversation_id,
                    user_id=user_id,
                    content=orion_response.get('response', 'Erro ao processar resposta'),
                    message_type=MessageType.AGENT,
                    agent_id=str(agent.id),
                    metadata={
                        'processing_time': orion_response.get('processing_time', 0),
                        'model_used': orion_response.get('model_used', ''),
                        'tokens_used': orion_response.get('tokens_used', 0),
                        'timestamp': datetime.utcnow()
                    },
                    created_at=datetime.utcnow()
                ),
                agent_name=agent.name,
                execution_time=orion_response.get('processing_time', 0),
                tokens_used=orion_response.get('tokens_used', 0)
            )
            
        except Exception as e:
            # Em caso de erro, criar mensagem de erro no MongoDB
            error_message_id = str(uuid.uuid4())
            error_message_data = {
                "id": error_message_id,
                "content": f"Erro ao processar mensagem: {str(e)}",
                "message_type": "system",
                "metadata": {
                    'error': True, 
                    'error_message': str(e),
                    'timestamp': datetime.utcnow()
                }
            }
            
            await add_messages_to_conversation(
                str(chat_request.conversation_id), 
                [error_message_data]
            )
            
            raise e
    
    def update_conversation(self, conversation_id: int, user_id: int, 
                          conversation_data: ConversationUpdate) -> Optional[ConversationResponse]:
        """
        Atualiza dados da conversação
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            conversation_data: Dados para atualização
            
        Returns:
            ConversationResponse ou None se não encontrada
        """
        # Preparar dados para atualização
        update_data = {}
        if conversation_data.title is not None:
            update_data['title'] = conversation_data.title
        if conversation_data.status is not None:
            update_data['status'] = conversation_data.status
        
        # Atualizar conversação
        conversation = self.chat_repository.update_conversation(conversation_id, user_id, **update_data)
        if not conversation:
            return None
        
        # Buscar nome do agente
        agent = self.agent_repository.get_agent_by_id(conversation.agent_id)
        agent_name = agent.name if agent else "Agente não encontrado"
        
        # Contar mensagens
        messages = self.chat_repository.get_conversation_messages(conversation_id, limit=1)
        
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            agent_name=agent_name,
            title=conversation.title,
            status=conversation.status,
            message_count=len(messages),
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at
        )
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Remove uma conversação
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            
        Returns:
            True se removida com sucesso
        """
        success = self.chat_repository.delete_conversation(conversation_id, user_id)
        
        if success:
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="conversation_deleted",
                description="Conversação removida"
            )
        
        return success
    
    def archive_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Arquiva uma conversação
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            
        Returns:
            True se arquivada com sucesso
        """
        success = self.chat_repository.archive_conversation(conversation_id, user_id)
        
        if success:
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="conversation_archived",
                description="Conversação arquivada"
            )
        
        return success
    
    def add_message_reaction(self, message_id: int, user_id: int, reaction_type: str) -> bool:
        """
        Adiciona reação a uma mensagem
        
        Args:
            message_id: ID da mensagem
            user_id: ID do usuário
            reaction_type: Tipo da reação
            
        Returns:
            True se adicionada com sucesso
        """
        try:
            self.chat_repository.create_message_reaction(message_id, user_id, reaction_type)
            return True
        except Exception:
            return False
    
    def remove_message_reaction(self, message_id: int, user_id: int) -> bool:
        """
        Remove reação de uma mensagem
        
        Args:
            message_id: ID da mensagem
            user_id: ID do usuário
            
        Returns:
            True se removida com sucesso
        """
        return self.chat_repository.remove_message_reaction(message_id, user_id)
    
    def get_conversation_context(self, conversation_id: int, user_id: int, 
                               context_type: str = None) -> List[Dict[str, Any]]:
        """
        Busca contexto da conversação
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            context_type: Tipo de contexto específico
            
        Returns:
            Lista de contextos
        """
        # Verificar se conversação pertence ao usuário
        conversation = self.chat_repository.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []
        
        contexts = self.chat_repository.get_conversation_context(conversation_id, context_type)
        
        return [
            {
                'id': context.id,
                'context_type': context.context_type,
                'context_data': context.context_data,
                'created_at': context.created_at
            }
            for context in contexts
        ]
    
    def get_chat_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Busca métricas de chat do usuário
        
        Args:
            user_id: ID do usuário
            days: Período em dias
            
        Returns:
            Métricas de chat
        """
        return self.chat_repository.get_user_chat_metrics(user_id, days)
    
    def search_conversations(self, user_id: int, query: str, limit: int = 50) -> List[ConversationSummary]:
        """
        Busca conversações por texto
        
        Args:
            user_id: ID do usuário
            query: Texto para busca
            limit: Limite de resultados
            
        Returns:
            Lista de conversações encontradas
        """
        # Para busca simples, usar o método de listar e filtrar no código
        conversations = self.chat_repository.get_user_conversations(user_id, limit=limit)
        
        # Filtrar conversações que contenham o texto na busca
        filtered = []
        query_lower = query.lower()
        
        for conv in conversations:
            if (query_lower in conv.title.lower() if conv.title else False):
                # Buscar nome do agente
                agent = self.agent_repository.get_agent_by_id(conv.agent_id)
                agent_name = agent.name if agent else "Agente não encontrado"
                
                # Contar mensagens (aproximado)
                messages = self.chat_repository.get_conversation_messages(conv.id, limit=1)
                
                filtered.append(ConversationSummary(
                    id=conv.id,
                    title=conv.title,
                    agent_name=agent_name,
                    message_count=len(messages),
                    last_message_at=conv.last_message_at,
                    created_at=conv.created_at
                ))
        
        return filtered

    def get_conversation_messages(self, conversation_id: str, user_id: int, limit: int = 100):
        """
        Busca mensagens de uma conversa específica
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário
            limit: Limite de mensagens
            
        Returns:
            Lista de mensagens
        """
        # Verificar se a conversa pertence ao usuário
        conversation = self.chat_repository.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversa não encontrada ou não pertence ao usuário")
        
        return self.chat_repository.get_conversation_messages(conversation_id, limit=limit)

    def create_message(self, conversation_id: str, user_id: str, content: str, 
                      message_type: str, agent_id: str = None):
        """
        Cria uma nova mensagem na conversa
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário
            content: Conteúdo da mensagem
            message_type: Tipo da mensagem ('user' ou 'agent')
            agent_id: ID do agente (opcional, para mensagens do agente)
            
        Returns:
            Message: Mensagem criada
        """
        from models.chat_models import MessageType
        
        # Verificar se a conversa pertence ao usuário
        conversation = self.chat_repository.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversa não encontrada ou não pertence ao usuário")
        
        # Converter string para enum
        msg_type = MessageType.USER if message_type == "user" else MessageType.AGENT
        
        # Criar mensagem
        message = self.chat_repository.create_message(
            conversation_id=conversation_id,
            content=content,
            message_type=msg_type,
            sender_id=user_id,
            agent_id=agent_id,
            message_metadata=None  # Não passar dicionário vazio
        )
        
        return message

    def update_conversation_timestamp(self, conversation_id: str):
        """
        Atualiza o timestamp da última mensagem da conversa
        
        Args:
            conversation_id: ID da conversa
        """
        # O timestamp já é atualizado automaticamente no repository.create_message
        # Este método é mantido para compatibilidade
        pass

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Remove uma conversa e todas suas mensagens
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário
            
        Returns:
            bool: True se removida com sucesso, False caso contrário
        """
        # Verificar se a conversa pertence ao usuário
        conversation = self.chat_repository.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversa não encontrada ou não pertence ao usuário")
        
        # Deletar conversa (mensagens são deletadas em cascade)
        success = self.chat_repository.delete_conversation(conversation_id, user_id)
        
        if success:
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="conversation_deleted",
                description=f"Conversa '{conversation.title}' foi removida"
            )
        
        return success
