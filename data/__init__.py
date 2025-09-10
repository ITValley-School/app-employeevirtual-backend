# data/__init__.py - VERSÃO ATUALIZADA
"""
Camada Data - inicialização do pacote com suporte híbrido SQL Server + MongoDB
"""

from .database import get_db, SessionLocal, engine
from .mongodb import (
    get_mongo_client, get_async_mongo_client, 
    get_database, get_async_database,
    Collections, create_indexes, test_mongodb_connection,
    create_chat_conversation, add_messages_to_conversation,
    get_conversation_history, update_conversation_context
)

__all__ = [
    # SQL Server
    'get_db',
    'SessionLocal', 
    'engine',
    
    # MongoDB
    'get_mongo_client',
    'get_async_mongo_client',
    'get_database',
    'get_async_database',
    'Collections',
    'create_indexes',
    'test_mongodb_connection',
    
    # Chat MongoDB
    'create_chat_conversation',
    'add_messages_to_conversation', 
    'get_conversation_history',
    'update_conversation_context'
]