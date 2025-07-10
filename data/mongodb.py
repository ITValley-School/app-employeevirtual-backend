"""
Configuração de conexão com MongoDB (para dados não-relacionais)
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional

# Configurações do MongoDB
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017"
)

MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "employeevirtual")

# Cliente síncrono
mongo_client: Optional[MongoClient] = None

# Cliente assíncrono
async_mongo_client: Optional[AsyncIOMotorClient] = None

def get_mongo_client() -> MongoClient:
    """
    Obtém cliente MongoDB síncrono
    
    Returns:
        MongoClient: Cliente MongoDB
    """
    global mongo_client
    
    if mongo_client is None:
        mongo_client = MongoClient(MONGODB_URL)
    
    return mongo_client

def get_async_mongo_client() -> AsyncIOMotorClient:
    """
    Obtém cliente MongoDB assíncrono
    
    Returns:
        AsyncIOMotorClient: Cliente MongoDB assíncrono
    """
    global async_mongo_client
    
    if async_mongo_client is None:
        async_mongo_client = AsyncIOMotorClient(MONGODB_URL)
    
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
    
    if async_mongo_client:
        async_mongo_client.close()
        async_mongo_client = None

# Collections utilizadas
class Collections:
    """Nomes das collections MongoDB"""
    
    # Logs e auditoria
    USER_ACTIVITIES = "user_activities"
    SYSTEM_LOGS = "system_logs"
    
    # Cache de sessões
    USER_SESSIONS = "user_sessions"
    
    # Dados temporários
    TEMP_FILES = "temp_files"
    
    # Métricas em tempo real
    REALTIME_METRICS = "realtime_metrics"
    
    # Configurações dinâmicas
    DYNAMIC_CONFIGS = "dynamic_configs"

async def create_indexes():
    """
    Cria índices necessários no MongoDB
    """
    db = get_async_database()
    
    # Índices para user_activities
    await db[Collections.USER_ACTIVITIES].create_index([("user_id", 1), ("created_at", -1)])
    await db[Collections.USER_ACTIVITIES].create_index([("activity_type", 1)])
    
    # Índices para user_sessions
    await db[Collections.USER_SESSIONS].create_index([("user_id", 1)])
    await db[Collections.USER_SESSIONS].create_index([("token", 1)], unique=True)
    await db[Collections.USER_SESSIONS].create_index([("expires_at", 1)], expireAfterSeconds=0)
    
    # Índices para system_logs
    await db[Collections.SYSTEM_LOGS].create_index([("level", 1), ("timestamp", -1)])
    await db[Collections.SYSTEM_LOGS].create_index([("service", 1)])
    
    # Índices para temp_files
    await db[Collections.TEMP_FILES].create_index([("user_id", 1)])
    await db[Collections.TEMP_FILES].create_index([("created_at", 1)], expireAfterSeconds=86400)  # 24 horas
    
    # Índices para realtime_metrics
    await db[Collections.REALTIME_METRICS].create_index([("user_id", 1), ("timestamp", -1)])
    await db[Collections.REALTIME_METRICS].create_index([("metric_type", 1)])

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

