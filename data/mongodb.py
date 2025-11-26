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
    Obtém cliente MongoDB síncrono com configurações otimizadas
    
    Returns:
        MongoClient: Cliente MongoDB
    """
    global mongo_client
    
    if mongo_client is None:
        try:
            # Configurações de timeout e retry para Azure Cosmos DB
            mongo_client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=10000,  # 10s para seleção de servidor
                socketTimeoutMS=30000,  # 30s para operações
                connectTimeoutMS=10000,  # 10s para conexão inicial
                retryWrites=True,
                retryReads=True,
                maxPoolSize=50,  # Pool de conexões
                minPoolSize=5,
                maxIdleTimeMS=45000,
            )
            # Testar conexão com timeout menor
            mongo_client.admin.command('ping', maxTimeMS=5000)
            logger.info("✅ Cliente MongoDB síncrono conectado")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MongoDB síncrono: {e}")
            # Não levanta exceção, permite que o sistema continue sem MongoDB
            # O repositório deve tratar erros graciosamente
            logger.warning("⚠️ Sistema continuará sem MongoDB. Algumas funcionalidades podem não funcionar.")
    
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
    AGENT_DOCUMENTS = "agent_documents"
    
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
        # Primeiro, buscar o documento atual para obter o message_count atual
        current_doc = await db[Collections.CHAT_CONVERSATIONS].find_one(
            {"_id": conversation_id},
            {"metadata.message_count": 1}
        )
        
        # Calcular novo message_count
        current_count = 0
        if current_doc and "metadata" in current_doc:
            current_count = current_doc["metadata"].get("message_count", 0)
            # Se for um objeto, usar 0
            if isinstance(current_count, dict):
                current_count = 0
        
        new_count = current_count + len(messages)
        
        result = await db[Collections.CHAT_CONVERSATIONS].update_one(
            {"_id": conversation_id},
            {
                "$push": {"messages": {"$each": mongo_messages}},
                "$set": {
                    "metadata.last_activity": datetime.utcnow(),
                    "metadata.message_count": new_count
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

async def get_user_conversations(user_id: str, limit: int = 20, skip: int = 0) -> list:
    """
    Busca conversas de um usuário
    
    Args:
        user_id: ID do usuário
        limit: Limite de conversas
        skip: Pular conversas
        
    Returns:
        Lista de conversas do usuário
    """
    db = get_async_database()
    
    try:
        cursor = db[Collections.CHAT_CONVERSATIONS].find(
            {"user_id": user_id},
            {
                "conversation_id": 1,
                "title": 1,
                "agent_id": 1,
                "metadata.last_activity": 1,
                "metadata.message_count": 1,
                "metadata.status": 1,
                "messages": {"$slice": 1}  # Apenas a primeira mensagem para preview
            }
        ).sort("metadata.last_activity", -1).skip(skip).limit(limit)
        
        conversations = []
        async for doc in cursor:
            conversations.append({
                "conversation_id": doc["conversation_id"],
                "title": doc.get("title", "Nova Conversa"),
                "agent_id": doc["agent_id"],
                "last_activity": doc["metadata"]["last_activity"],
                "message_count": doc["metadata"]["message_count"],
                "status": doc["metadata"]["status"],
                "preview": doc.get("messages", [{}])[0].get("content", "") if doc.get("messages") else ""
            })
        
        return conversations
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar conversas do usuário: {e}")
        return []

async def update_conversation_metadata(conversation_id: str, metadata_updates: Dict[str, Any]) -> bool:
    """
    Atualiza metadados de uma conversa
    
    Args:
        conversation_id: ID da conversa
        metadata_updates: Atualizações de metadados
        
    Returns:
        bool: True se sucesso
    """
    db = get_async_database()
    
    try:
        # Preparar atualizações de metadados
        set_updates = {}
        for key, value in metadata_updates.items():
            set_updates[f"metadata.{key}"] = value
        
        set_updates["metadata.last_activity"] = datetime.utcnow()
        
        result = await db[Collections.CHAT_CONVERSATIONS].update_one(
            {"_id": conversation_id},
            {"$set": set_updates}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar metadados: {e}")
        return False

async def delete_conversation(conversation_id: str) -> bool:
    """
    Remove uma conversa do MongoDB
    
    Args:
        conversation_id: ID da conversa
        
    Returns:
        bool: True se sucesso
    """
    db = get_async_database()
    
    try:
        result = await db[Collections.CHAT_CONVERSATIONS].delete_one(
            {"_id": conversation_id}
        )
        
        if result.deleted_count > 0:
            logger.info(f"✅ Conversa {conversation_id} removida do MongoDB")
            return True
        else:
            logger.warning(f"⚠️ Conversa {conversation_id} não encontrada para remoção")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao remover conversa: {e}")
        return False

async def get_conversation_analytics(conversation_id: str) -> Dict[str, Any]:
    """
    Busca analytics de uma conversa
    
    Args:
        conversation_id: ID da conversa
        
    Returns:
        Dict com analytics da conversa
    """
    db = get_async_database()
    
    try:
        conversation = await db[Collections.CHAT_CONVERSATIONS].find_one(
            {"_id": conversation_id},
            {
                "metadata": 1,
                "messages": 1
            }
        )
        
        if not conversation:
            return None
        
        messages = conversation.get("messages", [])
        metadata = conversation.get("metadata", {})
        
        # Calcular analytics
        user_messages = [msg for msg in messages if msg.get("message_type") == "user"]
        agent_messages = [msg for msg in messages if msg.get("message_type") == "agent"]
        
        total_tokens = sum(
            msg.get("metadata", {}).get("tokens_used", 0) 
            for msg in messages
        )
        
        total_cost = sum(
            msg.get("metadata", {}).get("cost", 0.0) 
            for msg in messages
        )
        
        avg_response_time = sum(
            msg.get("metadata", {}).get("execution_time", 0) 
            for msg in agent_messages
        ) / len(agent_messages) if agent_messages else 0
        
        return {
            "conversation_id": conversation_id,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "agent_messages": len(agent_messages),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_response_time": avg_response_time,
            "created_at": metadata.get("created_at"),
            "last_activity": metadata.get("last_activity"),
            "status": metadata.get("status")
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar analytics: {e}")
        return None

async def create_mongodb_indexes():
    """
    Cria índices otimizados para as collections de chat
    """
    db = get_async_database()
    
    try:
        # Índices para chat_conversations
        await db[Collections.CHAT_CONVERSATIONS].create_index([
            ("user_id", 1), ("metadata.last_activity", -1)
        ])
        
        await db[Collections.CHAT_CONVERSATIONS].create_index([
            ("agent_id", 1), ("metadata.status", 1)
        ])
        
        await db[Collections.CHAT_CONVERSATIONS].create_index([
            ("metadata.status", 1), ("metadata.created_at", -1)
        ])
        
        # Índices para chat_messages (backup)
        await db[Collections.CHAT_MESSAGES].create_index([
            ("conversation_id", 1), ("timestamp", -1)
        ])
        
        await db[Collections.CHAT_MESSAGES].create_index([
            ("user_id", 1), ("message_type", 1)
        ])
        
        logger.info("✅ Índices MongoDB criados com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar índices MongoDB: {e}")
        raise