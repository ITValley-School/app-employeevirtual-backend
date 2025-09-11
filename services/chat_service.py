"""
Serviço de chat/conversação para o sistema EmployeeVirtual - Nova implementação
Usa apenas repository para acesso a dados
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from data.chat_repository import ChatRepository
from data.agent_repository import AgentRepository
from data.user_repository import UserRepository
from models.chat_models import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse, ChatRequest, ChatResponse,
    ConversationWithMessages, ConversationSummary, MessageType, ConversationStatus
)
from services.orion_service import OrionService


class ChatService:
    """Serviço para gerenciamento de chat/conversação - Nova implementação"""
    
    def __init__(self, db: Session):
        self.chat_repository = ChatRepository(db)
        self.agent_repository = AgentRepository(db)
        self.user_repository = UserRepository(db)
        self.orion_service = OrionService()
    
    def create_conversation(self, user_id: str, conversation_data: ConversationCreate) -> ConversationResponse:
        """
        Cria uma nova conversação
        
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
        
        # Criar conversação
        conversation = self.chat_repository.create_conversation(
            user_id=user_id,
            agent_id=conversation_data.agent_id,
            title=conversation_data.title or f"Conversa com {agent.name}"
        )
        
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
    
    def get_user_conversations(self, user_id: int, limit: int = 50) -> List[ConversationSummary]:
        """
        Busca conversações do usuário
        
        Args:
            user_id: ID do usuário
            limit: Limite de conversações
            
        Returns:
            Lista de resumos de conversações
        """
        summaries = self.chat_repository.get_conversation_summaries(user_id, limit)
        
        result = []
        for summary in summaries:
            # Buscar nome do agente
            agent = self.agent_repository.get_agent_by_id(summary['agent_id'])
            agent_name = agent.name if agent else "Agente não encontrado"
            
            result.append(ConversationSummary(
                id=summary['id'],
                title=summary['title'],
                agent_name=agent_name,
                message_count=summary['message_count'],
                last_message_at=summary['last_message_at'],
                created_at=summary['created_at']
            ))
        
        return result
    
    def get_conversation_with_messages(self, conversation_id: int, user_id: int, 
                                     message_limit: int = 50) -> Optional[ConversationWithMessages]:
        """
        Busca conversação com suas mensagens
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            message_limit: Limite de mensagens
            
        Returns:
            ConversationWithMessages ou None se não encontrada
        """
        conversation = self.chat_repository.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        
        # Buscar mensagens
        messages = self.chat_repository.get_conversation_messages(
            conversation_id, limit=message_limit, order_desc=False
        )
        
        # Buscar nome do agente
        agent = self.agent_repository.get_agent_by_id(conversation.agent_id)
        agent_name = agent.name if agent else "Agente não encontrado"
        
        # Converter mensagens
        message_responses = []
        for msg in messages:
            message_responses.append(MessageResponse(
                id=msg.id,
                content=msg.content,
                message_type=msg.message_type,
                sender_id=msg.sender_id,
                agent_id=msg.agent_id,
                message_metadata=msg.message_metadata,
                created_at=msg.created_at
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
    
    def send_message(self, user_id: int, message_data: MessageCreate) -> MessageResponse:
        """
        Envia uma mensagem em uma conversação
        
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
        
        # Criar mensagem do usuário
        user_message = self.chat_repository.create_message(
            conversation_id=message_data.conversation_id,
            content=message_data.content,
            message_type=MessageType.USER,
            sender_id=user_id,
            message_metadata=message_data.message_metadata
        )
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="message_sent",
            description=f"Mensagem enviada na conversa '{conversation.title}'"
        )
        
        return MessageResponse(
            id=user_message.id,
            content=user_message.content,
            message_type=user_message.message_type,
            sender_id=user_message.sender_id,
            agent_id=user_message.agent_id,
            message_metadata=user_message.message_metadata,
            created_at=user_message.created_at
        )
    
    async def process_chat_request(self, user_id: int, chat_request: ChatRequest) -> ChatResponse:
        """
        Processa uma requisição de chat completa
        
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
            
            # Criar mensagem do usuário
            user_message = self.chat_repository.create_message(
                conversation_id=chat_request.conversation_id,
                content=chat_request.message,
                message_type=MessageType.USER,
                sender_id=user_id
            )
            
            # Buscar histórico de mensagens para contexto
            recent_messages = self.chat_repository.get_recent_messages(
                chat_request.conversation_id, minutes=60
            )
            
            # Preparar contexto para o agente
            context_messages = []
            for msg in recent_messages[-10:]:  # Últimas 10 mensagens
                role = "user" if msg.message_type == MessageType.USER else "assistant"
                context_messages.append({
                    "role": role,
                    "content": msg.content
                })
            
            # Adicionar mensagem atual
            context_messages.append({
                "role": "user",
                "content": chat_request.message
            })
            
            # Chamar serviço Orion para processar com o agente
            orion_response = await self.orion_service.process_with_agent(
                agent_id=agent.id,
                messages=context_messages,
                user_id=user_id,
                conversation_id=chat_request.conversation_id
            )
            
            # Criar mensagem de resposta do agente
            agent_message = self.chat_repository.create_message(
                conversation_id=chat_request.conversation_id,
                content=orion_response.get('response', 'Erro ao processar resposta'),
                message_type=MessageType.AGENT,
                agent_id=agent.id,
                message_metadata={
                    'processing_time': orion_response.get('processing_time', 0),
                    'model_used': orion_response.get('model_used', ''),
                    'tokens_used': orion_response.get('tokens_used', 0)
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
                    id=user_message.id,
                    content=user_message.content,
                    message_type=user_message.message_type,
                    sender_id=user_message.sender_id,
                    agent_id=user_message.agent_id,
                    message_metadata=user_message.message_metadata,
                    created_at=user_message.created_at
                ),
                agent_response=MessageResponse(
                    id=agent_message.id,
                    content=agent_message.content,
                    message_type=agent_message.message_type,
                    sender_id=agent_message.sender_id,
                    agent_id=agent_message.agent_id,
                    message_metadata=agent_message.message_metadata,
                    created_at=agent_message.created_at
                ),
                processing_time=orion_response.get('processing_time', 0)
            )
            
        except Exception as e:
            # Em caso de erro, ainda criar mensagem de erro
            error_message = self.chat_repository.create_message(
                conversation_id=chat_request.conversation_id,
                content=f"Erro ao processar mensagem: {str(e)}",
                message_type=MessageType.SYSTEM,
                message_metadata={'error': True, 'error_message': str(e)}
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
