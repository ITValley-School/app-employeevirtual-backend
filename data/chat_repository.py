"""
Repositório de chat/conversação para o sistema EmployeeVirtual
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_

from models.chat_models import (
    Conversation, Message, ConversationContext, MessageReaction,
    MessageType, ConversationStatus
)


class ChatRepository:
    """Repositório para operações de dados de chat/conversação"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD Conversações
    def create_conversation(self, user_id: int, agent_id: int, title: str = None) -> Conversation:
        """Cria uma nova conversação"""
        db_conversation = Conversation(
            user_id=user_id,
            agent_id=agent_id,
            title=title
        )
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation
    
    def get_conversation_by_id(self, conversation_id: int, user_id: int = None) -> Optional[Conversation]:
        """Busca conversação por ID"""
        query = self.db.query(Conversation).filter(Conversation.id == conversation_id)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        return query.first()
    
    def get_user_conversations(self, user_id: int, skip: int = 0, limit: int = 50, 
                              status: ConversationStatus = None) -> List[Conversation]:
        """Busca conversações do usuário"""
        query = self.db.query(Conversation).filter(Conversation.user_id == user_id)
        
        if status:
            query = query.filter(Conversation.status == status)
        
        return query.order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
    
    def get_conversation_summaries(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca resumos de conversações com contagem de mensagens"""
        results = self.db.query(
            Conversation.id,
            Conversation.title,
            Conversation.agent_id,
            Conversation.created_at,
            Conversation.last_message_at,
            Conversation.status,
            func.count(Message.id).label('message_count')
        ).outerjoin(Message).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == ConversationStatus.ACTIVE
            )
        ).group_by(
            Conversation.id,
            Conversation.title,
            Conversation.agent_id,
            Conversation.created_at,
            Conversation.last_message_at,
            Conversation.status
        ).order_by(desc(Conversation.last_message_at)).limit(limit).all()
        
        return [
            {
                'id': result.id,
                'title': result.title,
                'agent_id': result.agent_id,
                'created_at': result.created_at,
                'last_message_at': result.last_message_at,
                'status': result.status,
                'message_count': result.message_count or 0
            }
            for result in results
        ]
    
    def update_conversation(self, conversation_id: int, user_id: int, **kwargs) -> Optional[Conversation]:
        """Atualiza dados da conversação"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        
        for key, value in kwargs.items():
            if hasattr(conversation, key) and value is not None:
                setattr(conversation, key, value)
        
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def update_conversation_last_message(self, conversation_id: int) -> bool:
        """Atualiza timestamp da última mensagem"""
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return False
        
        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Remove conversação"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        # Remover mensagens relacionadas primeiro
        self.db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        
        # Remover conversação
        self.db.delete(conversation)
        self.db.commit()
        return True
    
    def archive_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Arquiva conversação"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        conversation.status = ConversationStatus.ARCHIVED
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    # CRUD Mensagens
    def create_message(self, conversation_id: int, content: str, message_type: MessageType,
                      sender_id: int = None, agent_id: int = None, 
                      message_metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Cria uma nova mensagem"""
        db_message = Message(
            conversation_id=conversation_id,
            content=content,
            message_type=message_type,
            sender_id=sender_id,
            agent_id=agent_id,
            message_metadata=message_metadata or {}
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        # Atualizar timestamp da conversação
        self.update_conversation_last_message(conversation_id)
        
        return db_message
    
    def get_message_by_id(self, message_id: int) -> Optional[Message]:
        """Busca mensagem por ID"""
        return self.db.query(Message).filter(Message.id == message_id).first()
    
    def get_conversation_messages(self, conversation_id: int, skip: int = 0, 
                                 limit: int = 50, order_desc: bool = False) -> List[Message]:
        """Busca mensagens de uma conversação"""
        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)
        
        if order_desc:
            query = query.order_by(desc(Message.created_at))
        else:
            query = query.order_by(Message.created_at)
        
        return query.offset(skip).limit(limit).all()
    
    def get_recent_messages(self, conversation_id: int, minutes: int = 60) -> List[Message]:
        """Busca mensagens recentes de uma conversação"""
        since_time = datetime.utcnow() - timedelta(minutes=minutes)
        return self.db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.created_at >= since_time
            )
        ).order_by(Message.created_at).all()
    
    def get_messages_by_type(self, conversation_id: int, message_type: MessageType) -> List[Message]:
        """Busca mensagens por tipo"""
        return self.db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.message_type == message_type
            )
        ).order_by(Message.created_at).all()
    
    def update_message(self, message_id: int, **kwargs) -> Optional[Message]:
        """Atualiza dados da mensagem"""
        message = self.get_message_by_id(message_id)
        if not message:
            return None
        
        for key, value in kwargs.items():
            if hasattr(message, key) and value is not None:
                setattr(message, key, value)
        
        message.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def delete_message(self, message_id: int) -> bool:
        """Remove mensagem"""
        message = self.get_message_by_id(message_id)
        if not message:
            return False
        
        self.db.delete(message)
        self.db.commit()
        return True
    
    # CRUD Contexto de Conversação
    def create_conversation_context(self, conversation_id: int, context_type: str,
                                   context_data: Dict[str, Any]) -> ConversationContext:
        """Cria contexto para conversação"""
        db_context = ConversationContext(
            conversation_id=conversation_id,
            context_type=context_type,
            context_data=context_data
        )
        self.db.add(db_context)
        self.db.commit()
        self.db.refresh(db_context)
        return db_context
    
    def get_conversation_context(self, conversation_id: int, context_type: str = None) -> List[ConversationContext]:
        """Busca contexto da conversação"""
        query = self.db.query(ConversationContext).filter(
            ConversationContext.conversation_id == conversation_id
        )
        
        if context_type:
            query = query.filter(ConversationContext.context_type == context_type)
        
        return query.order_by(desc(ConversationContext.created_at)).all()
    
    def update_conversation_context(self, context_id: int, context_data: Dict[str, Any]) -> Optional[ConversationContext]:
        """Atualiza contexto da conversação"""
        context = self.db.query(ConversationContext).filter(ConversationContext.id == context_id).first()
        if not context:
            return None
        
        context.context_data = context_data
        context.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(context)
        return context
    
    # CRUD Reações
    def create_message_reaction(self, message_id: int, user_id: int, reaction_type: str) -> MessageReaction:
        """Cria reação para mensagem"""
        # Verificar se já existe reação do usuário para esta mensagem
        existing_reaction = self.db.query(MessageReaction).filter(
            and_(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id
            )
        ).first()
        
        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_reaction)
            return existing_reaction
        
        db_reaction = MessageReaction(
            message_id=message_id,
            user_id=user_id,
            reaction_type=reaction_type
        )
        self.db.add(db_reaction)
        self.db.commit()
        self.db.refresh(db_reaction)
        return db_reaction
    
    def remove_message_reaction(self, message_id: int, user_id: int) -> bool:
        """Remove reação da mensagem"""
        reaction = self.db.query(MessageReaction).filter(
            and_(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id
            )
        ).first()
        
        if not reaction:
            return False
        
        self.db.delete(reaction)
        self.db.commit()
        return True
    
    def get_message_reactions(self, message_id: int) -> List[MessageReaction]:
        """Busca reações da mensagem"""
        return self.db.query(MessageReaction).filter(
            MessageReaction.message_id == message_id
        ).all()
    
    # Estatísticas e relatórios
    def get_conversation_stats(self, conversation_id: int) -> Dict[str, Any]:
        """Busca estatísticas da conversação"""
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return {}
        
        # Contagem de mensagens por tipo
        message_stats = self.db.query(
            Message.message_type,
            func.count(Message.id).label('count')
        ).filter(
            Message.conversation_id == conversation_id
        ).group_by(Message.message_type).all()
        
        message_counts = {stat.message_type: stat.count for stat in message_stats}
        
        # Primeira e última mensagem
        first_message = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).first()
        
        last_message = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).first()
        
        return {
            'conversation_id': conversation_id,
            'title': conversation.title,
            'status': conversation.status,
            'created_at': conversation.created_at,
            'updated_at': conversation.updated_at,
            'message_counts': message_counts,
            'total_messages': sum(message_counts.values()),
            'first_message_at': first_message.created_at if first_message else None,
            'last_message_at': last_message.created_at if last_message else None
        }
    
    def get_user_chat_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Busca métricas de chat do usuário"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Conversações ativas
        active_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == ConversationStatus.ACTIVE
            )
        ).count()
        
        # Mensagens enviadas
        messages_sent = self.db.query(Message).join(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Message.message_type == MessageType.USER,
                Message.created_at >= since_date
            )
        ).count()
        
        # Mensagens recebidas
        messages_received = self.db.query(Message).join(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Message.message_type == MessageType.AGENT,
                Message.created_at >= since_date
            )
        ).count()
        
        return {
            'user_id': user_id,
            'period_days': days,
            'active_conversations': active_conversations,
            'messages_sent': messages_sent,
            'messages_received': messages_received,
            'total_messages': messages_sent + messages_received
        }
