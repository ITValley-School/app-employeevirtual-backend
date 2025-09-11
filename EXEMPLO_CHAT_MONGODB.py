# Exemplo: chat_repository.py MIGRADO PARA MONGODB

"""
Repositório de chat/conversação para o sistema EmployeeVirtual - VERSÃO MONGODB
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from bson import ObjectId
import uuid

from data.mongodb import get_mongo_client  # ✅ Importar MongoDB
from models.chat_models import (
    MessageType, ConversationStatus, ConversationResponse, MessageResponse
)


class ChatRepository:
    """Repositório para operações de dados de chat/conversação - MONGODB"""
    
    def __init__(self, db: Session):
        self.db = db  # Manter para compatibilidade (caso precise de dados relacionais)
        
        # ✅ MUDANÇA PRINCIPAL: Usar MongoDB para chat
        self.mongo_client = get_mongo_client()
        self.mongo_db = self.mongo_client.employeevirtual
        self.conversations = self.mongo_db.conversations  # Collection de conversas
        self.messages = self.mongo_db.messages           # Collection de mensagens
    
    # ✅ CRUD Conversações - AGORA NO MONGODB
    def create_conversation(self, user_id: str, agent_id: str, title: str = None) -> Dict[str, Any]:
        """Cria uma nova conversação no MongoDB"""
        conversation_data = {
            "_id": str(uuid.uuid4()),  # Usar UUID como string
            "user_id": user_id,
            "agent_id": agent_id, 
            "title": title or f"Conversa com {agent_id}",
            "status": ConversationStatus.ACTIVE.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "message_count": 0,
            "metadata": {}
        }
        
        # ✅ Inserir no MongoDB
        result = self.conversations.insert_one(conversation_data)
        conversation_data["_id"] = str(result.inserted_id)
        return conversation_data
    
    def get_conversation_by_id(self, conversation_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Busca conversação por ID no MongoDB"""
        query = {"_id": conversation_id}
        if user_id:
            query["user_id"] = user_id
        
        # ✅ Buscar no MongoDB
        return self.conversations.find_one(query)
    
    def get_user_conversations(self, user_id: str, skip: int = 0, limit: int = 50, 
                              status: ConversationStatus = None) -> List[Dict[str, Any]]:
        """Busca conversações do usuário no MongoDB"""
        query = {"user_id": user_id}
        
        if status:
            query["status"] = status.value
        
        # ✅ Buscar no MongoDB com paginação
        cursor = self.conversations.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        return list(cursor)
    
    def update_conversation(self, conversation_id: str, update_data: Dict[str, Any]) -> bool:
        """Atualiza conversação no MongoDB"""
        update_data["updated_at"] = datetime.now()
        
        # ✅ Atualizar no MongoDB
        result = self.conversations.update_one(
            {"_id": conversation_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Remove conversação do MongoDB"""
        # ✅ Remover conversação e suas mensagens
        conv_result = self.conversations.delete_one({
            "_id": conversation_id,
            "user_id": user_id
        })
        
        # Remover mensagens associadas
        self.messages.delete_many({"conversation_id": conversation_id})
        
        return conv_result.deleted_count > 0
    
    # ✅ CRUD Mensagens - AGORA NO MONGODB
    def create_message(self, conversation_id: str, content: str, message_type: MessageType,
                      sender_id: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cria nova mensagem no MongoDB"""
        message_data = {
            "_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "content": content,
            "type": message_type.value,
            "sender_id": sender_id,
            "created_at": datetime.now(),
            "metadata": metadata or {},
            "reactions": []
        }
        
        # ✅ Inserir mensagem no MongoDB
        result = self.messages.insert_one(message_data)
        
        # ✅ Atualizar contador de mensagens na conversação
        self.conversations.update_one(
            {"_id": conversation_id},
            {
                "$inc": {"message_count": 1},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        message_data["_id"] = str(result.inserted_id)
        return message_data
    
    def get_conversation_messages(self, conversation_id: str, skip: int = 0, 
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """Busca mensagens da conversação no MongoDB"""
        # ✅ Buscar mensagens no MongoDB
        cursor = self.messages.find(
            {"conversation_id": conversation_id}
        ).sort("created_at", 1).skip(skip).limit(limit)
        
        return list(cursor)
    
    def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Busca mensagem por ID no MongoDB"""
        return self.messages.find_one({"_id": message_id})
    
    def update_message(self, message_id: str, update_data: Dict[str, Any]) -> bool:
        """Atualiza mensagem no MongoDB"""
        # ✅ Atualizar no MongoDB
        result = self.messages.update_one(
            {"_id": message_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_message(self, message_id: str) -> bool:
        """Remove mensagem do MongoDB"""
        message = self.get_message_by_id(message_id)
        if not message:
            return False
        
        # ✅ Remover mensagem
        result = self.messages.delete_one({"_id": message_id})
        
        # ✅ Decrementar contador na conversação
        if result.deleted_count > 0:
            self.conversations.update_one(
                {"_id": message["conversation_id"]},
                {"$inc": {"message_count": -1}}
            )
        
        return result.deleted_count > 0
    
    # ✅ Métodos de busca avançada (aproveitando MongoDB)
    def search_messages(self, user_id: str, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca mensagens por texto usando índice do MongoDB"""
        # Buscar conversações do usuário
        user_conversations = self.get_user_conversations(user_id, limit=1000)
        conversation_ids = [conv["_id"] for conv in user_conversations]
        
        # ✅ Busca por texto no MongoDB
        cursor = self.messages.find({
            "conversation_id": {"$in": conversation_ids},
            "$text": {"$search": query}
        }).limit(limit)
        
        return list(cursor)
    
    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Estatísticas da conversação usando agregação do MongoDB"""
        # ✅ Usar pipeline de agregação do MongoDB
        pipeline = [
            {"$match": {"conversation_id": conversation_id}},
            {"$group": {
                "_id": "$type",
                "count": {"$sum": 1},
                "last_message": {"$max": "$created_at"}
            }}
        ]
        
        stats = list(self.messages.aggregate(pipeline))
        
        return {
            "message_types": {stat["_id"]: stat["count"] for stat in stats},
            "total_messages": sum(stat["count"] for stat in stats),
            "last_activity": max((stat["last_message"] for stat in stats), default=None)
        }
    
    # ✅ Método para migração (se necessário)
    def migrate_conversation_from_sql(self, sql_conversation_id: str) -> str:
        """Migra uma conversação específica do SQL para MongoDB"""
        # Buscar dados do SQL
        sql_conv = self.db.query(ConversationEntity).filter(
            ConversationEntity.id == sql_conversation_id
        ).first()
        
        if not sql_conv:
            return None
        
        # Criar no MongoDB
        mongo_conv = self.create_conversation(
            user_id=sql_conv.user_id,
            agent_id=sql_conv.agent_id,
            title=sql_conv.title
        )
        
        # Migrar mensagens
        sql_messages = self.db.query(MessageEntity).filter(
            MessageEntity.conversation_id == sql_conversation_id
        ).all()
        
        for sql_msg in sql_messages:
            self.create_message(
                conversation_id=mongo_conv["_id"],
                content=sql_msg.content,
                message_type=MessageType(sql_msg.type),
                sender_id=sql_msg.sender_id,
                metadata=sql_msg.metadata or {}
            )
        
        return mongo_conv["_id"]


# ✅ EXEMPLO DE USO - Service não muda nada!
"""
# O ChatService continua exatamente igual:

class ChatService:
    def __init__(self, db: Session):
        self.chat_repository = ChatRepository(db)  # ✅ Mesmo código!
    
    def create_conversation(self, user_id: str, agent_id: str):
        # ✅ Mesma interface, mas agora usa MongoDB internamente
        return self.chat_repository.create_conversation(user_id, agent_id)
"""
