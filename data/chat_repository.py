"""
Repositório de chat/conversação para o sistema EmployeeVirtual
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_

from data.entities.chat_entities import (
    ConversationEntity, MessageEntity, ConversationContextEntity, MessageReactionEntity
)
from models.chat_models import (
    MessageType, ConversationStatus
)


class ChatRepository:
    """Repositório para operações de dados de chat/conversação"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD Conversações
    def create_conversation(self, user_id: str, agent_id: str, title: str = None) -> ConversationEntity:
        """Cria uma nova conversação"""
        db_conversation = ConversationEntity(
            user_id=user_id,
            agent_id=agent_id,
            title=title
        )
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation
    
    def get_conversation_by_id(self, conversation_id: str, user_id: str = None) -> Optional[ConversationEntity]:
        """Busca conversação por ID"""
        query = self.db.query(ConversationEntity).filter(ConversationEntity.id == conversation_id)
        if user_id:
            query = query.filter(ConversationEntity.user_id == user_id)
        return query.first()
    
    def get_user_conversations(self, user_id: str, skip: int = 0, limit: int = 50, 
                              status: ConversationStatus = None) -> List[ConversationEntity]:
        """Busca conversações do usuário"""
        query = self.db.query(ConversationEntity).filter(ConversationEntity.user_id == user_id)
        
        if status:
            query = query.filter(ConversationEntity.status == status)
        
        return query.order_by(desc(ConversationEntity.updated_at)).offset(skip).limit(limit).all()
    
    def get_conversation_summaries(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca resumos de conversações com contagem de mensagens"""
        results = self.db.query(
            ConversationEntity.id,
            ConversationEntity.title,
            ConversationEntity.agent_id,
            ConversationEntity.created_at,
            ConversationEntity.last_message_at,
            ConversationEntity.status,
            func.count(MessageEntity.id).label('message_count')
        ).outerjoin(MessageEntity).filter(
            and_(
                ConversationEntity.user_id == user_id,
                ConversationEntity.status == ConversationStatus.ACTIVE
            )
        ).group_by(
            ConversationEntity.id,
            ConversationEntity.title,
            ConversationEntity.agent_id,
            ConversationEntity.created_at,
            ConversationEntity.last_message_at,
            ConversationEntity.status
        ).order_by(desc(ConversationEntity.last_message_at)).limit(limit).all()
        
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
    
    def update_conversation(self, conversation_id: int, user_id: int, **kwargs) -> Optional[ConversationEntity]:
        """Atualiza dados da conversação"""
        ConversationEntity = self.get_conversation_by_id(conversation_id, user_id)
        if not ConversationEntity:
            return None
        
        for key, value in kwargs.items():
            if hasattr(ConversationEntity, key) and value is not None:
                setattr(ConversationEntity, key, value)
        
        ConversationEntity.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ConversationEntity)
        return ConversationEntity
    
    def update_conversation_last_message(self, conversation_id: int) -> bool:
        """Atualiza timestamp da última mensagem"""
        ConversationEntity = self.db.query(ConversationEntity).filter(ConversationEntity.id == conversation_id).first()
        if not ConversationEntity:
            return False
        
        ConversationEntity.last_message_at = datetime.utcnow()
        ConversationEntity.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Remove conversação"""
        ConversationEntity = self.get_conversation_by_id(conversation_id, user_id)
        if not ConversationEntity:
            return False
        
        # Remover mensagens relacionadas primeiro
        self.db.query(MessageEntity).filter(MessageEntity.conversation_id == conversation_id).delete()
        
        # Remover conversação
        self.db.delete(ConversationEntity)
        self.db.commit()
        return True
    
    def archive_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Arquiva conversação"""
        ConversationEntity = self.get_conversation_by_id(conversation_id, user_id)
        if not ConversationEntity:
            return False
        
        ConversationEntity.status = ConversationStatus.ARCHIVED
        ConversationEntity.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    # CRUD Mensagens
    def create_message(self, conversation_id: str, content: str, message_type: MessageType,
                      sender_id: str = None, agent_id: str = None, 
                      message_metadata: Optional[Dict[str, Any]] = None) -> MessageEntity:
        """Cria uma nova mensagem"""
        import json
        
        # Converter metadata para JSON string se fornecido
        metadata_json = None
        if message_metadata:
            metadata_json = json.dumps(message_metadata)
        
        db_message = MessageEntity(
            conversation_id=conversation_id,
            user_id=sender_id,
            content=content,
            message_type=message_type,
            agent_id=agent_id,
            message_metadata=metadata_json
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        # Atualizar timestamp da conversação
        self.update_conversation_last_message(conversation_id)
        
        return db_message
    
    def get_message_by_id(self, message_id: int) -> Optional[MessageEntity]:
        """Busca mensagem por ID"""
        return self.db.query(MessageEntity).filter(MessageEntity.id == message_id).first()
    
    def get_conversation_messages(self, conversation_id: int, skip: int = 0, 
                                 limit: int = 50, order_desc: bool = False) -> List[MessageEntity]:
        """Busca mensagens de uma conversação"""
        query = self.db.query(MessageEntity).filter(MessageEntity.conversation_id == conversation_id)
        
        if order_desc:
            query = query.order_by(desc(MessageEntity.created_at))
        else:
            query = query.order_by(MessageEntity.created_at)
        
        return query.offset(skip).limit(limit).all()
    
    def get_recent_messages(self, conversation_id: int, minutes: int = 60) -> List[MessageEntity]:
        """Busca mensagens recentes de uma conversação"""
        since_time = datetime.utcnow() - timedelta(minutes=minutes)
        return self.db.query(MessageEntity).filter(
            and_(
                MessageEntity.conversation_id == conversation_id,
                MessageEntity.created_at >= since_time
            )
        ).order_by(MessageEntity.created_at).all()
    
    def get_messages_by_type(self, conversation_id: int, message_type: MessageType) -> List[MessageEntity]:
        """Busca mensagens por tipo"""
        return self.db.query(MessageEntity).filter(
            and_(
                MessageEntity.conversation_id == conversation_id,
                MessageEntity.message_type == message_type
            )
        ).order_by(MessageEntity.created_at).all()
    
    def update_message(self, message_id: int, **kwargs) -> Optional[MessageEntity]:
        """Atualiza dados da mensagem"""
        MessageEntity = self.get_message_by_id(message_id)
        if not MessageEntity:
            return None
        
        for key, value in kwargs.items():
            if hasattr(MessageEntity, key) and value is not None:
                setattr(MessageEntity, key, value)
        
        MessageEntity.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(MessageEntity)
        return MessageEntity
    
    def delete_message(self, message_id: int) -> bool:
        """Remove mensagem"""
        MessageEntity = self.get_message_by_id(message_id)
        if not MessageEntity:
            return False
        
        self.db.delete(MessageEntity)
        self.db.commit()
        return True
    
    # CRUD Contexto de Conversação
    def create_conversation_context(self, conversation_id: int, context_type: str,
                                   context_data: Dict[str, Any]) -> ConversationContextEntity:
        """Cria contexto para conversação"""
        db_context = ConversationContextEntity(
            conversation_id=conversation_id,
            context_type=context_type,
            context_data=context_data
        )
        self.db.add(db_context)
        self.db.commit()
        self.db.refresh(db_context)
        return db_context
    
    def get_conversation_context(self, conversation_id: int, context_type: str = None) -> List[ConversationContextEntity]:
        """Busca contexto da conversação"""
        query = self.db.query(ConversationContextEntity).filter(
            ConversationContextEntity.conversation_id == conversation_id
        )
        
        if context_type:
            query = query.filter(ConversationContextEntity.context_type == context_type)
        
        return query.order_by(desc(ConversationContextEntity.created_at)).all()
    
    def update_conversation_context(self, context_id: int, context_data: Dict[str, Any]) -> Optional[ConversationContextEntity]:
        """Atualiza contexto da conversação"""
        context = self.db.query(ConversationContextEntity).filter(ConversationContextEntity.id == context_id).first()
        if not context:
            return None
        
        context.context_data = context_data
        context.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(context)
        return context
    
    # CRUD Reações
    def create_message_reaction(self, message_id: int, user_id: int, reaction_type: str) -> MessageReactionEntity:
        """Cria reação para mensagem"""
        # Verificar se já existe reação do usuário para esta mensagem
        existing_reaction = self.db.query(MessageReactionEntity).filter(
            and_(
                MessageReactionEntity.message_id == message_id,
                MessageReactionEntity.user_id == user_id
            )
        ).first()
        
        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_reaction)
            return existing_reaction
        
        db_reaction = MessageReactionEntity(
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
        reaction = self.db.query(MessageReactionEntity).filter(
            and_(
                MessageReactionEntity.message_id == message_id,
                MessageReactionEntity.user_id == user_id
            )
        ).first()
        
        if not reaction:
            return False
        
        self.db.delete(reaction)
        self.db.commit()
        return True
    
    def get_message_reactions(self, message_id: int) -> List[MessageReactionEntity]:
        """Busca reações da mensagem"""
        return self.db.query(MessageReactionEntity).filter(
            MessageReactionEntity.message_id == message_id
        ).all()
    
    # Estatísticas e relatórios
    def get_conversation_stats(self, conversation_id: int) -> Dict[str, Any]:
        """Busca estatísticas da conversação"""
        ConversationEntity = self.db.query(ConversationEntity).filter(ConversationEntity.id == conversation_id).first()
        if not ConversationEntity:
            return {}
        
        # Contagem de mensagens por tipo
        message_stats = self.db.query(
            MessageEntity.message_type,
            func.count(MessageEntity.id).label('count')
        ).filter(
            MessageEntity.conversation_id == conversation_id
        ).group_by(MessageEntity.message_type).all()
        
        message_counts = {stat.message_type: stat.count for stat in message_stats}
        
        # Primeira e última mensagem
        first_message = self.db.query(MessageEntity).filter(
            MessageEntity.conversation_id == conversation_id
        ).order_by(MessageEntity.created_at).first()
        
        last_message = self.db.query(MessageEntity).filter(
            MessageEntity.conversation_id == conversation_id
        ).order_by(desc(MessageEntity.created_at)).first()
        
        return {
            'conversation_id': conversation_id,
            'title': ConversationEntity.title,
            'status': ConversationEntity.status,
            'created_at': ConversationEntity.created_at,
            'updated_at': ConversationEntity.updated_at,
            'message_counts': message_counts,
            'total_messages': sum(message_counts.values()),
            'first_message_at': first_message.created_at if first_message else None,
            'last_message_at': last_message.created_at if last_message else None
        }
    
    def get_user_chat_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Busca métricas de chat do usuário"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Conversações ativas
        active_conversations = self.db.query(ConversationEntity).filter(
            and_(
                ConversationEntity.user_id == user_id,
                ConversationEntity.status == ConversationStatus.ACTIVE
            )
        ).count()
        
        # Mensagens enviadas
        messages_sent = self.db.query(MessageEntity).join(ConversationEntity).filter(
            and_(
                ConversationEntity.user_id == user_id,
                MessageEntity.message_type == MessageType.USER,
                MessageEntity.created_at >= since_date
            )
        ).count()
        
        # Mensagens recebidas
        messages_received = self.db.query(MessageEntity).join(ConversationEntity).filter(
            and_(
                ConversationEntity.user_id == user_id,
                MessageEntity.message_type == MessageType.AGENT,
                MessageEntity.created_at >= since_date
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
