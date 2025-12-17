"""
Repositório para execuções de agentes de sistema no MongoDB
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from data.mongodb import get_database, Collections

logger = logging.getLogger(__name__)


class SystemAgentExecutionRepository:
    """Repositório para execuções de agentes de sistema no MongoDB"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db[Collections.AGENT_EXECUTIONS]
    
    def save_execution(
        self,
        system_agent_id: str,
        user_id: str,
        user_message: str,
        agent_response: str,
        tools_used: List[str],
        execution_metadata: Dict[str, Any]
    ) -> str:
        """
        Salva execução de agente de sistema
        
        Args:
            system_agent_id: ID do agente de sistema
            user_id: ID do usuário
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            tools_used: Lista de ferramentas usadas
            execution_metadata: Metadados adicionais (tokens, tempo, etc)
            
        Returns:
            str: ID da execução salva
        """
        try:
            execution_doc = {
                "system_agent_id": system_agent_id,
                "user_id": user_id,
                "user_message": user_message,
                "agent_response": agent_response,
                "tools_used": tools_used or [],
                "execution_metadata": execution_metadata or {},
                "created_at": datetime.utcnow(),
                "session_id": execution_metadata.get("session_id")
            }
            
            result = self.collection.insert_one(execution_doc)
            logger.info(f"✅ Execução salva no MongoDB: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar execução: {str(e)}", exc_info=True)
            # Retorna ID vazio em caso de erro (não quebra o fluxo)
            return ""
    
    def get_execution_history(
        self,
        system_agent_id: str,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Busca histórico de execuções
        
        Args:
            system_agent_id: ID do agente de sistema
            user_id: ID do usuário (opcional, filtra por usuário)
            limit: Limite de resultados
            
        Returns:
            Lista de execuções
        """
        try:
            query = {"system_agent_id": system_agent_id}
            if user_id:
                query["user_id"] = user_id
            
            executions = list(
                self.collection.find(query)
                .sort("created_at", -1)
                .limit(limit)
                .max_time_ms(5000)  # Timeout de 5s
            )
            
            for exec in executions:
                exec["_id"] = str(exec["_id"])
                exec["id"] = str(exec["_id"])
            
            return executions
        except Exception as e:
            logger.error(f"❌ Erro ao buscar histórico: {str(e)}", exc_info=True)
            return []

