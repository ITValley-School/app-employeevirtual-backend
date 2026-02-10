"""
Repositório para cache de resultados de tools no MongoDB
"""
import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from data.mongodb import get_database, Collections

logger = logging.getLogger(__name__)


class ToolCacheRepository:
    """Cache de resultados de tools no MongoDB"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db[Collections.CACHE_DATA]
    
    def _generate_cache_key(
        self,
        tool_type: str,
        input_data: Dict[str, Any]
    ) -> str:
        """Gera chave de cache baseada no tipo e input"""
        # Normaliza input para gerar hash consistente
        normalized = json.dumps(input_data, sort_keys=True)
        hash_key = hashlib.md5(normalized.encode()).hexdigest()
        return f"tool:{tool_type}:{hash_key}"
    
    def get_cached_result(
        self,
        tool_type: str,
        input_data: Dict[str, Any],
        ttl_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Busca resultado em cache
        
        Args:
            tool_type: Tipo da tool (transcribe_audio, ocr_image, etc)
            input_data: Dados de entrada (URL, file_hash, etc)
            ttl_hours: Tempo de vida do cache em horas
            
        Returns:
            Resultado em cache ou None
        """
        try:
            cache_key = self._generate_cache_key(tool_type, input_data)
            
            cached = self.collection.find_one({
                "cache_key": cache_key,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if cached:
                logger.info(f"✅ Cache hit para {tool_type}")
                return cached.get("result")
            
            return None
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar cache: {str(e)}")
            return None
    
    def save_cached_result(
        self,
        tool_type: str,
        input_data: Dict[str, Any],
        result: Dict[str, Any],
        ttl_hours: int = 24
    ) -> str:
        """
        Salva resultado no cache
        
        Args:
            tool_type: Tipo da tool
            input_data: Dados de entrada
            result: Resultado da tool
            ttl_hours: Tempo de vida do cache
            
        Returns:
            Chave do cache
        """
        try:
            cache_key = self._generate_cache_key(tool_type, input_data)
            
            cache_doc = {
                "cache_key": cache_key,
                "tool_type": tool_type,
                "input_data": input_data,
                "result": result,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=ttl_hours)
            }
            
            # Upsert: atualiza se existir, cria se não existir
            self.collection.update_one(
                {"cache_key": cache_key},
                {"$set": cache_doc},
                upsert=True
            )
            
            logger.info(f"✅ Resultado salvo no cache: {cache_key}")
            return cache_key
        except Exception as e:
            logger.warning(f"⚠️ Erro ao salvar cache: {str(e)}")
            return ""

