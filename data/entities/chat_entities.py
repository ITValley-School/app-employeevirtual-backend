"""
Entidades de Chat - EmployeeVirtual
Seguindo padrão IT Valley Architecture
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from typing import Any

from data.base import Base

# Configuração de schema baseada no tipo de banco
USE_SCHEMA = True  # Usar schema para Azure SQL
SCHEMA_CONFIG = {'schema': 'empl'} if USE_SCHEMA else {}


class ChatSessionEntity(Base):
    """Entidade de sessão de chat"""
    __tablename__ = "chat_sessions"
    __table_args__ = SCHEMA_CONFIG

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    agent_id = Column(String(36), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, closed, archived
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<ChatSessionEntity(id={self.id}, user_id={self.user_id}, title={self.title})>"


class ChatMessageEntity(Base):
    """Entidade de mensagem de chat"""
    __tablename__ = "chat_messages"
    __table_args__ = SCHEMA_CONFIG

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey('empl.chat_sessions.id'), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    message = Column(Text, nullable=False)
    sender = Column(String(20), nullable=False)  # user, assistant
    context = Column(Text, nullable=True)  # JSON string de contexto
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<ChatMessageEntity(id={self.id}, session_id={self.session_id}, sender={self.sender})>"
