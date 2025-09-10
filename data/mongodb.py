# data/mongodb.py - VERSÃO MELHORADA
"""
Configuração de conexão com MongoDB (para dados não-relacionais)
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurações do MongoDB
MONGODB_URL = os.getenv(
    "MONGODB_URL"
)

MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "employeevirtual")

# Cliente síncrono
mongo_client: Optional[MongoClient] = None

# Cliente assíncrono
async_mongo_client: Optional[AsyncIOMotorClient] = None

logger = logging.getLogger(__name__)

def get_mongo_client() -> MongoClient:
    """
    Obtém cliente MongoDB síncrono
    
    Returns:
        MongoClient: Cliente MongoDB
    """
    global mongo_client
    
    if mongo_client is None:
        try:
            mongo_client = MongoClient(MONGODB_URL)
            # Testar conexão
            mongo_client.admin.command('ping')
            logger.info("✅ Cliente MongoDB síncrono conectado")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MongoDB síncrono: {e}")
            raise
    
    return mongo_client

def get_async_mongo_client() -> AsyncIOMotorClient:
    """
    Obtém cliente MongoDB assíncrono
    
    Returns:
        AsyncIOMotorClient: Cliente MongoDB assíncrono
    """
    global async_mongo_client
    
    if async_mongo_client is None:
        try:
            async_mongo_client = AsyncIOMotorClient(MONGODB_URL)
            logger.info("✅ Cliente MongoDB assíncrono criado")
        except Exception as e:
            logger.error(f"❌ Erro ao criar cliente MongoDB assíncrono: {e}")
            raise
    
    return async_mongo_client

def get_database():
    """
    Obtém database MongoDB síncrono
    
    Returns:
        Database: Database MongoDB
    """
    client = get_mongo_client()
    return client[MONGODB_DATABASE]

def get_async_database():
    """
    Obtém database MongoDB assíncrono
    
    Returns:
        AsyncIOMotorDatabase: Database MongoDB assíncrono
    """
    client = get_async_mongo_client()
    return client[MONGODB_DATABASE]

def close_mongo_connections():
    """
    Fecha conexões MongoDB
    """
    global mongo_client, async_mongo_client
    
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        logger.info("🔒 Cliente MongoDB síncrono fechado")
    
    if async_mongo_client:
        async_mongo_client.close()
        async_mongo_client = None
        logger.info("🔒 Cliente MongoDB assíncrono fechado")

# Collections utilizadas - EXPANDIDO
class Collections:
    """Nomes das collections MongoDB"""
    
    # === CHAT E CONVERSAS ===
    CHAT_CONVERSATIONS = "chat_conversations"
    CHAT_MESSAGES = "chat_messages"
    CHAT_ANALYTICS = "chat_analytics"
    CHAT_SESSIONS = "chat_sessions"
    
    # === AGENTES E IA ===
    AGENT_EXECUTIONS = "agent_executions"
    AGENT_METRICS = "agent_metrics"
    AGENT_KNOWLEDGE = "agent_knowledge"
    
    # === USUÁRIOS E SESSÕES ===
    USER_ACTIVITIES = "user_activities"
    USER_SESSIONS = "user_sessions"
    USER_METRICS = "user_metrics"
    USER_PREFERENCES = "user_preferences"
    
    # === SISTEMA E LOGS ===
    SYSTEM_LOGS = "system_logs"
    SYSTEM_METRICS = "system_metrics"
    SYSTEM_CONFIGS = "system_configs"
    
    # === ARQUIVOS E PROCESSAMENTO ===
    FILE_PROCESSING = "file_processing"
    FILE_METADATA = "file_metadata"
    ORION_JOBS = "orion_jobs"
    
    # === FLOWS E AUTOMAÇÃO ===
    FLOW_EXECUTIONS = "flow_executions"
    FLOW_METRICS = "flow_metrics"
    FLOW_TEMPLATES = "flow_templates"
    
    # === CACHE E TEMPORÁRIOS ===
    CACHE_DATA = "cache_data"
    TEMP_FILES = "temp_files"
    TEMP_SESSIONS = "temp_sessions"
    
    # === MÉTRICAS E ANALYTICS ===
    REALTIME_METRICS = "realtime_metrics"
    DAILY_METRICS = "daily_metrics"
    WEEKLY_METRICS = "weekly_metrics"
    MONTHLY_METRICS = "monthly_metrics"
    
    # === CONFIGURAÇÕES DINÂMICAS ===
    DYNAMIC_CONFIGS = "dynamic_configs"

async def create_indexes():
    """
    Cria índices necessários no MongoDB
    """
    db = get_async_database()
    
    logger.info("🚀 Criando índices MongoDB...")
    
    # === ÍNDICES DE CHAT ===
    # Chat Conversations
    await db[Collections.CHAT_CONVERSATIONS].create_index([
        ("user_id", 1), ("metadata.last_activity", -1)
    ])
    await db[Collections.CHAT_CONVERSATIONS].create_index([
        ("agent_id", 1), ("metadata.status", 1)
    ])
    await db[Collections.CHAT_CONVERSATIONS].create_index([
        ("metadata.status", 1), ("metadata.created_at", -1)
    ])
    
    # Chat Messages
    await db[Collections.CHAT_MESSAGES].create_index([
        ("conversation_id", 1), ("timestamp", -1)
    ])
    await db[Collections.CHAT_MESSAGES].create_index([
        ("user_id", 1), ("message_type", 1)
    ])
    await db[Collections.CHAT_MESSAGES].create_index([
        ("agent_id", 1), ("timestamp", -1)
    ])
    
    # Chat Analytics
    await db[Collections.CHAT_ANALYTICS].create_index([
        ("user_id", 1), ("date", -1)
    ])
    await db[Collections.CHAT_ANALYTICS].create_index([
        ("agent_id", 1), ("date", -1)
    ])
    
    # === ÍNDICES DE USUÁRIOS ===
    # User Activities
    await db[Collections.USER_ACTIVITIES].create_index([
        ("user_id", 1), ("created_at", -1)
    ])
    await db[Collections.USER_ACTIVITIES].create_index([
        ("activity_type", 1)
    ])
    
    # User Sessions
    await db[Collections.USER_SESSIONS].create_index([
        ("user_id", 1)
    ])
    await db[Collections.USER_SESSIONS].create_index([
        ("token", 1)
    ], unique=True)
    await db[Collections.USER_SESSIONS].create_index([
        ("expires_at", 1)
    ], expireAfterSeconds=0)
    
    # User Metrics
    await db[Collections.USER_METRICS].create_index([
        ("user_id", 1), ("date", -1)
    ])
    
    # === ÍNDICES DE SISTEMA ===
    # System Logs
    await db[Collections.SYSTEM_LOGS].create_index([
        ("level", 1), ("timestamp", -1)
    ])
    await db[Collections.SYSTEM_LOGS].create_index([
        ("service", 1)
    ])
    
    # === ÍNDICES DE ARQUIVOS ===
    # Temp Files
    await db[Collections.TEMP_FILES].create_index([
        ("user_id", 1)
    ])
    await db[Collections.TEMP_FILES].create_index([
        ("created_at", 1)
    ], expireAfterSeconds=86400)  # 24 horas
    
    # === ÍNDICES DE MÉTRICAS ===
    # Realtime Metrics
    await db[Collections.REALTIME_METRICS].create_index([
        ("user_id", 1), ("timestamp", -1)
    ])
    await db[Collections.REALTIME_METRICS].create_index([
        ("metric_type", 1)
    ])
    
    # Agent Executions
    await db[Collections.AGENT_EXECUTIONS].create_index([
        ("agent_id", 1), ("created_at", -1)
    ])
    await db[Collections.AGENT_EXECUTIONS].create_index([
        ("user_id", 1), ("created_at", -1)
    ])
    await db[Collections.AGENT_EXECUTIONS].create_index([
        ("success", 1), ("created_at", -1)
    ])
    
    logger.info("✅ Todos os índices MongoDB criados")

async def test_mongodb_connection() -> Dict[str, Any]:
    """
    Testa conexão com MongoDB
    
    Returns:
        Dict com informações da conexão
    """
    try:
        db = get_async_database()
        
        # Testar ping
        await db.command('ping')
        
        # Obter informações do servidor
        server_info = await db.command('buildInfo')
        
        # Listar collections
        collections = await db.list_collection_names()
        
        return {
            "connected": True,
            "server_version": server_info.get("version"),
            "database": MONGODB_DATABASE,
            "collections_count": len(collections),
            "collections": collections[:10]  # Primeiras 10 collections
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão MongoDB: {e}")
        return {
            "connected": False,
            "error": str(e)
        }

def get_connection_info():
    """
    Retorna informações da conexão MongoDB
    
    Returns:
        Dict com informações da conexão
    """
    try:
        client = get_mongo_client()
        server_info = client.server_info()
        
        return {
            "connected": True,
            "server_version": server_info.get("version"),
            "database": MONGODB_DATABASE,
            "collections": client[MONGODB_DATABASE].list_collection_names()
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }

# === UTILITÁRIOS PARA CHAT ===

async def create_chat_conversation(conversation_data: Dict[str, Any]) -> str:
    """
    Cria uma nova conversa de chat no MongoDB
    
    Args:
        conversation_data: Dados da conversa
        
    Returns:
        str: ID da conversa criada
    """
    db = get_async_database()
    
    conversation_doc = {
        "_id": conversation_data["conversation_id"],
        "conversation_id": conversation_data["conversation_id"],
        "user_id": conversation_data["user_id"],
        "agent_id": conversation_data["agent_id"],
        "title": conversation_data.get("title", "Nova Conversa"),
        "messages": [],
        "context": conversation_data.get("context", {}),
        "metadata": {
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "message_count": 0,
            "status": "active",
            "total_tokens": 0,
            "total_cost": 0.0
        }
    }
    
    result = await db[Collections.CHAT_CONVERSATIONS].insert_one(conversation_doc)
    logger.info(f"✅ Conversa criada no MongoDB: {conversation_data['conversation_id']}")
    
    return str(result.inserted_id)

async def add_messages_to_conversation(conversation_id: str, messages: list) -> bool:
    """
    Adiciona mensagens a uma conversa existente
    
    Args:
        conversation_id: ID da conversa
        messages: Lista de mensagens
        
    Returns:
        bool: True se sucesso
    """
    db = get_async_database()
    
    try:
        # Preparar mensagens para inserção
        mongo_messages = []
        for msg in messages:
            mongo_msg = {
                "id": msg.get("id"),
                "content": msg["content"],
                "message_type": msg["message_type"],
                "user_id": msg.get("user_id"),
                "agent_id": msg.get("agent_id"),
                "metadata": msg.get("metadata", {}),
                "timestamp": datetime.utcnow()
            }
            mongo_messages.append(mongo_msg)
        
        # Atualizar documento (atômico)
        result = await db[Collections.CHAT_CONVERSATIONS].update_one(
            {"_id": conversation_id},
            {
                "$push": {"messages": {"$each": mongo_messages}},
                "$set": {
                    "metadata.last_activity": datetime.utcnow(),
                    "metadata.message_count": {"$add": ["$metadata.message_count", len(messages)]}
                }
            }
        )
        
        if result.modified_count == 0:
            logger.error(f"❌ Conversa {conversation_id} não encontrada no MongoDB")
            return False
        
        logger.info(f"✅ {len(messages)} mensagens adicionadas à conversa {conversation_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar mensagens: {e}")
        return False

async def get_conversation_history(conversation_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Busca histórico de uma conversa
    
    Args:
        conversation_id: ID da conversa
        limit: Limite de mensagens
        
    Returns:
        Dict com histórico da conversa
    """
    db = get_async_database()
    
    try:
        conversation = await db[Collections.CHAT_CONVERSATIONS].find_one(
            {"_id": conversation_id},
            {
                "messages": {"$slice": -limit},  # Últimas N mensagens
                "context": 1,
                "metadata": 1
            }
        )
        
        if not conversation:
            return None
        
        return {
            "conversation_id": conversation["_id"],
            "messages": conversation.get("messages", []),
            "context": conversation.get("context", {}),
            "metadata": conversation.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico: {e}")
        return None

async def update_conversation_context(conversation_id: str, context: Dict[str, Any]) -> bool:
    """
    Atualiza contexto de uma conversa
    
    Args:
        conversation_id: ID da conversa
        context: Novo contexto
        
    Returns:
        bool: True se sucesso
    """
    db = get_async_database()
    
    try:
        result = await db[Collections.CHAT_CONVERSATIONS].update_one(
            {"_id": conversation_id},
            {
                "$set": {
                    "context": context,
                    "metadata.last_activity": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar contexto: {e}")
        return False