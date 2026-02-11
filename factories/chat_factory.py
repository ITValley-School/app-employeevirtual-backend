"""
Factory para chat
Cria objetos do domínio seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4

from schemas.chat.requests import ChatMessageRequest, ChatSessionRequest
from domain.chat.chat_entity import ChatEntity


class ChatFactory:
    """Factory para criação de chat"""

    @staticmethod
    def create_session(dto: ChatSessionRequest, user_id: str) -> ChatEntity:
        """Cria sessão de chat"""
        return ChatEntity(
            id=str(uuid4()),
            title=dto.title,
            user_id=user_id,
            agent_id=dto.agent_id,
            status="active",
            created_at=datetime.utcnow()
        )

    @staticmethod
    def create_message(dto: ChatMessageRequest, session_id: str, user_id: str) -> ChatEntity:
        """Cria mensagem de chat"""
        return ChatEntity(
            id=str(uuid4()),
            session_id=session_id,
            user_id=user_id,
            message=dto.message,
            sender="user",
            context=dto.context,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def create_assistant_message(response_text: str, session_id: str, user_id: str) -> ChatEntity:
        """Cria mensagem de resposta do assistente"""
        return ChatEntity(
            id=str(uuid4()),
            session_id=session_id,
            user_id=user_id,
            message=response_text,
            sender="assistant",
            context={},
            created_at=datetime.utcnow()
        )

    @staticmethod
    def message_from(dto) -> str:
        """Extrai texto da mensagem do DTO"""
        if hasattr(dto, 'message'):
            return dto.message or ""
        if isinstance(dto, dict):
            return dto.get('message', "")
        return ""

    # ========== HELPERS PARA SESSION DTO ==========

    @staticmethod
    def agent_id_from(dto) -> Optional[str]:
        """Extrai agent_id do DTO de sessão"""
        if hasattr(dto, 'agent_id'):
            return dto.agent_id
        if isinstance(dto, dict):
            return dto.get('agent_id')
        return None

    # ========== HELPERS PARA ENTITY ==========

    @staticmethod
    def id_from(entity) -> str:
        """Extrai ID de uma entidade de chat"""
        return getattr(entity, 'id', '')

    @staticmethod
    def agent_id_from_session(session) -> Optional[str]:
        """Extrai agent_id de uma sessão"""
        return getattr(session, 'agent_id', None)

    @staticmethod
    def title_from(session) -> str:
        """Extrai título de uma sessão"""
        return getattr(session, 'title', 'Nova Conversa') or 'Nova Conversa'

    @staticmethod
    def created_at_from(entity) -> Optional[datetime]:
        """Extrai created_at de uma entidade"""
        return getattr(entity, 'created_at', None)

    # ========== HELPERS PARA MONGODB ==========

    @staticmethod
    def to_mongo_message(entity: ChatEntity, session_id: str, user_id: str, agent_id: str, extra_metadata: dict = None) -> dict:
        """Converte ChatEntity para formato MongoDB de mensagem"""
        result = {
            'session_id': session_id,
            'user_id': user_id,
            'agent_id': agent_id,
            'message': entity.message,
            'sender': entity.sender,
            'context': entity.context or {},
            'metadata': {
                'message_id': entity.id,
                'created_at': entity.created_at,
            }
        }
        if extra_metadata:
            result['metadata'].update(extra_metadata)
        return result

    @staticmethod
    def to_mongo_conversation(session: ChatEntity, user_id: str) -> dict:
        """Converte sessão para formato MongoDB de conversa"""
        return {
            'conversation_id': session.id,
            'user_id': user_id,
            'agent_id': session.agent_id,
            'title': session.title or 'Nova Conversa',
            'context': {}
        }

    @staticmethod
    def to_mongo_message_dict(session_id: str, user_id: str, agent_id: str, message: str, sender: str) -> dict:
        """Constrói dict de mensagem para MongoDB a partir de dados primitivos"""
        return {
            'session_id': session_id,
            'user_id': user_id,
            'agent_id': agent_id,
            'message': message,
            'sender': sender,
            'context': {},
            'metadata': {
                'created_at': datetime.utcnow(),
                'source': 'agent_execute'
            }
        }

    @staticmethod
    def from_mongo_message(msg: dict) -> ChatEntity:
        """Converte dict do MongoDB para ChatEntity"""
        return ChatEntity(
            id=msg.get('id') or str(msg.get('_id', '')),
            session_id=msg.get('session_id', ''),
            user_id=msg.get('user_id', ''),
            message=msg.get('message', ''),
            sender=msg.get('sender', 'user'),
            context=msg.get('context', {}),
            created_at=msg.get('created_at')
        )

    @staticmethod
    def from_mongo_conversation(conv: dict, agent_id: str, user_id: str) -> dict:
        """Converte conversa do MongoDB para formato de sidebar"""
        metadata = conv.get('metadata', {})
        status = metadata.get('status', 'active')
        return {
            'id': conv.get('conversation_id', ''),
            'title': conv.get('title', 'Nova Conversa'),
            'agent_id': agent_id,
            'user_id': user_id,
            'last_activity': metadata.get('last_activity'),
            'message_count': metadata.get('message_count', 0),
            'status': status,
            'created_at': metadata.get('created_at'),
        }
