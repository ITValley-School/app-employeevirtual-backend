"""
Serviço de chat/conversação para o sistema EmployeeVirtual
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from models.chat_models import (
    Conversation, Message, ConversationContext, MessageReaction,
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse, ChatRequest, ChatResponse,
    ConversationWithMessages, ConversationSummary, MessageType, ConversationStatus
)
from models.user_models import UserActivity
from services.agent_service import AgentService


class ChatService:
    """Serviço para gerenciamento de chat/conversação"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService(db)
    
    def create_conversation(self, user_id: int, conversation_data: ConversationCreate) -> ConversationResponse:
        """
        Cria uma nova conversação
        
        Args:
            user_id: ID do usuário
            conversation_data: Dados da conversação
            
        Returns:
            ConversationResponse: Dados da conversação criada
        """
        # Verificar se agente existe e pertence ao usuário
        agent = self.agent_service.get_agent_by_id(conversation_data.agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        db_conversation = Conversation(
            user_id=user_id,
            agent_id=conversation_data.agent_id,
            title=conversation_data.title or f"Conversa com {agent.name}"
        )
        
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "conversation_created", 
            f"Nova conversa iniciada com agente '{agent.name}'"
        )
        
        return ConversationResponse(
            id=db_conversation.id,
            user_id=db_conversation.user_id,
            agent_id=db_conversation.agent_id,
            agent_name=agent.name,
            title=db_conversation.title,
            status=db_conversation.status,
            message_count=0,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
            last_message_at=db_conversation.last_message_at
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
        # Query com join para buscar nome do agente e última mensagem
        conversations = self.db.query(
            Conversation.id,
            Conversation.title,
            Conversation.created_at,
            Conversation.last_message_at,
            func.count(Message.id).label('message_count')
        ).outerjoin(Message).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == ConversationStatus.ACTIVE
            )
        ).group_by(
            Conversation.id,
            Conversation.title,
            Conversation.created_at,
            Conversation.last_message_at
        ).order_by(desc(Conversation.last_message_at)).limit(limit).all()
        
        result = []
        for conv in conversations:
            # Buscar última mensagem
            last_message = self.db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(desc(Message.created_at)).first()
            
            # Buscar nome do agente
            conversation_obj = self.db.query(Conversation).filter(
                Conversation.id == conv.id
            ).first()
            
            agent = self.agent_service.get_agent_by_id(conversation_obj.agent_id)
            
            result.append(ConversationSummary(
                id=conv.id,
                title=conv.title or f"Conversa com {agent.name if agent else 'Agente'}",
                agent_name=agent.name if agent else "Agente",
                message_count=conv.message_count,
                last_message_preview=last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else (last_message.content if last_message else ""),
                last_message_at=conv.last_message_at or conv.created_at,
                created_at=conv.created_at
            ))
        
        return result
    
    def get_conversation_with_messages(self, conversation_id: int, user_id: int, limit: int = 100) -> Optional[ConversationWithMessages]:
        """
        Busca conversação com mensagens
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            limit: Limite de mensagens
            
        Returns:
            ConversationWithMessages ou None se não encontrada
        """
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return None
        
        # Buscar mensagens
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).limit(limit).all()
        
        # Buscar nome do agente
        agent = self.agent_service.get_agent_by_id(conversation.agent_id)
        
        # Contar mensagens
        message_count = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()
        
        return ConversationWithMessages(
            id=conversation.id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            agent_name=agent.name if agent else "Agente",
            title=conversation.title,
            status=conversation.status,
            message_count=message_count,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at,
            messages=[
                MessageResponse(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    user_id=msg.user_id,
                    agent_id=msg.agent_id,
                    content=msg.content,
                    message_type=msg.message_type,
                    metadata=json.loads(msg.message_metadata) if msg.message_metadata else None,
                    created_at=msg.created_at,
                    edited_at=msg.edited_at,
                    is_edited=msg.is_edited
                )
                for msg in messages
            ]
        )
    
    async def send_message(self, user_id: int, chat_request: ChatRequest) -> ChatResponse:
        """
        Envia mensagem e obtém resposta do agente
        
        Args:
            user_id: ID do usuário
            chat_request: Dados da mensagem
            
        Returns:
            ChatResponse: Resposta do chat
        """
        # Verificar se agente existe
        agent = self.agent_service.get_agent_by_id(chat_request.agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Buscar ou criar conversação
        if chat_request.conversation_id:
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.id == chat_request.conversation_id,
                    Conversation.user_id == user_id
                )
            ).first()
            
            if not conversation:
                raise ValueError("Conversação não encontrada")
        else:
            # Criar nova conversação
            conversation = Conversation(
                user_id=user_id,
                agent_id=chat_request.agent_id,
                title=f"Conversa com {agent.name}"
            )
            self.db.add(conversation)
            self.db.flush()  # Para obter o ID
        
        # Salvar mensagem do usuário
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            content=chat_request.message,
            message_type=MessageType.USER,
            message_metadata=json.dumps(chat_request.context) if chat_request.context else None
        )
        
        self.db.add(user_message)
        self.db.flush()
        
        # Executar agente
        agent_result = await self.agent_service.execute_agent(
            agent_id=chat_request.agent_id,
            user_id=user_id,
            user_message=chat_request.message,
            context=chat_request.context
        )
        
        # Salvar resposta do agente
        agent_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            agent_id=chat_request.agent_id,
            content=agent_result["response"],
            message_type=MessageType.AGENT,
            message_metadata=json.dumps({
                "execution_time": agent_result.get("execution_time"),
                "model_used": agent_result.get("model_used"),
                "success": agent_result.get("success")
            })
        )
        
        self.db.add(agent_message)
        
        # Atualizar conversação
        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(agent_message)
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "chat_message_sent", 
            f"Mensagem enviada para agente '{agent.name}'"
        )
        
        return ChatResponse(
            conversation_id=conversation.id,
            user_message=MessageResponse.from_orm(user_message),
            agent_response=MessageResponse.from_orm(agent_message),
            agent_name=agent.name,
            execution_time=agent_result.get("execution_time"),
            tokens_used=agent_result.get("tokens_used")
        )
    
    def update_conversation(self, conversation_id: int, user_id: int, conversation_data: ConversationUpdate) -> Optional[ConversationResponse]:
        """
        Atualiza conversação
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            conversation_data: Dados a serem atualizados
            
        Returns:
            ConversationResponse atualizada ou None se não encontrada
        """
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return None
        
        # Atualizar campos fornecidos
        update_data = conversation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)
        
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(conversation)
        
        # Buscar nome do agente
        agent = self.agent_service.get_agent_by_id(conversation.agent_id)
        
        # Contar mensagens
        message_count = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()
        
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            agent_name=agent.name if agent else "Agente",
            title=conversation.title,
            status=conversation.status,
            message_count=message_count,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at
        )
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Deleta conversação (soft delete)
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            
        Returns:
            True se deletada com sucesso
        """
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return False
        
        conversation.status = ConversationStatus.DELETED
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "conversation_deleted", 
            f"Conversação '{conversation.title}' deletada"
        )
        
        return True
    
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
        # Verificar se mensagem existe e pertence ao usuário
        message = self.db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.user_id == user_id
            )
        ).first()
        
        if not message:
            return False
        
        # Verificar se já existe reação do usuário para esta mensagem
        existing_reaction = self.db.query(MessageReaction).filter(
            and_(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id
            )
        ).first()
        
        if existing_reaction:
            # Atualizar reação existente
            existing_reaction.reaction_type = reaction_type
        else:
            # Criar nova reação
            reaction = MessageReaction(
                message_id=message_id,
                user_id=user_id,
                reaction_type=reaction_type
            )
            self.db.add(reaction)
        
        self.db.commit()
        
        return True
    
    def get_conversation_context(self, conversation_id: int, user_id: int) -> Dict[str, Any]:
        """
        Busca contexto da conversação
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            
        Returns:
            Dicionário com contexto
        """
        # Verificar se conversação pertence ao usuário
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return {}
        
        # Buscar contextos
        contexts = self.db.query(ConversationContext).filter(
            ConversationContext.conversation_id == conversation_id
        ).all()
        
        return {
            context.context_key: context.context_value
            for context in contexts
        }
    
    def set_conversation_context(self, conversation_id: int, user_id: int, context_key: str, context_value: str) -> bool:
        """
        Define contexto da conversação
        
        Args:
            conversation_id: ID da conversação
            user_id: ID do usuário
            context_key: Chave do contexto
            context_value: Valor do contexto
            
        Returns:
            True se definido com sucesso
        """
        # Verificar se conversação pertence ao usuário
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return False
        
        # Buscar contexto existente
        existing_context = self.db.query(ConversationContext).filter(
            and_(
                ConversationContext.conversation_id == conversation_id,
                ConversationContext.context_key == context_key
            )
        ).first()
        
        if existing_context:
            # Atualizar contexto existente
            existing_context.context_value = context_value
            existing_context.updated_at = datetime.utcnow()
        else:
            # Criar novo contexto
            context = ConversationContext(
                conversation_id=conversation_id,
                context_key=context_key,
                context_value=context_value
            )
            self.db.add(context)
        
        self.db.commit()
        
        return True
    
    def _log_user_activity(self, user_id: int, activity_type: str, description: str):
        """Registra atividade do usuário"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description
        )
        
        self.db.add(activity)
        # Não fazer commit aqui, deixar para o método principal

