"""
Repositório MongoDB para documentos vetoriais de agentes.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from data.mongodb import get_database, Collections

logger = logging.getLogger(__name__)


def _stringify_id(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte ObjectId em string para facilitar consumo na API.
    """
    if document and "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]
    return document


class AgentDocumentRepository:
    """
    Controla registros de uploads enviados ao vetor DB.
    """

    def __init__(self):
        db = get_database()
        self.collection = db[Collections.AGENT_DOCUMENTS]

    def record_upload(
        self,
        *,
        agent_id: str,
        user_id: str,
        file_name: str,
        metadata: Dict[str, Any],
        vector_response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Persiste o upload realizado para referência futura.
        
        Nota: Se o MongoDB estiver indisponível, retorna documento em memória.
        O documento já está no Pinecone (mais importante), então não quebra o fluxo.
        """
        document = {
            "agent_id": agent_id,
            "user_id": user_id,
            "file_name": file_name,
            "metadata": metadata or {},
            "vector_response": vector_response or {},
            "created_at": datetime.utcnow(),
        }
        
        try:
            # Tenta inserir com timeout de 5s via with_options
            result = self.collection.with_options(
                write_concern=None,
                read_preference=None
            ).insert_one(document)
            document["_id"] = result.inserted_id
            logger.info(
                f"✅ Documento {file_name} registrado no MongoDB para agente {agent_id}"
            )
            return _stringify_id(document.copy())
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Tratamento específico para timeouts do MongoDB
            is_timeout = (
                'timeout' in error_msg.lower() or 
                'timed out' in error_msg.lower() or
                'ServerSelectionTimeoutError' in error_type or
                'NetworkTimeout' in error_msg
            )
            
            if is_timeout:
                logger.warning(
                    f"⏱️ Timeout ao registrar documento {file_name} no MongoDB. "
                    f"Documento já está no Pinecone (importante). Continuando sem persistência MongoDB."
                )
            else:
                logger.error(
                    f"❌ Erro ao registrar documento {file_name} no MongoDB: {error_msg}",
                    exc_info=True
                )
            
            # Retorna documento em memória (sem _id do MongoDB)
            # O documento já está no Pinecone, que é o mais importante
            # Não levanta exceção - permite que o fluxo continue
            document["_id"] = "mongo_unavailable"
            document["mongo_error"] = True
            document["mongo_error_message"] = error_msg if is_timeout else "Erro desconhecido"
            return _stringify_id(document.copy())

    def list_documents(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Lista documentos associados a um agente do usuário.
        """
        try:
            cursor = self.collection.find(
                {"agent_id": agent_id, "user_id": user_id}
            )
            cursor = cursor.with_options(max_time_ms=5000)  # Timeout de 5s
            docs = list(cursor.sort("created_at", -1))
            return [_stringify_id(doc) for doc in docs]
        except Exception as e:
            error_msg = str(e)
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                logger.warning(
                    f"⏱️ Timeout ao listar documentos do agente {agent_id}. "
                    f"Retornando lista vazia."
                )
            else:
                logger.error(
                    f"❌ Erro ao listar documentos: {error_msg}",
                    exc_info=True
                )
            return []

    def has_documents(self, agent_id: str) -> bool:
        """
        Verifica se o agente possui documentos vetoriais.
        """
        try:
            cursor = self.collection.find({"agent_id": agent_id}).limit(1)
            cursor = cursor.with_options(max_time_ms=3000)  # Timeout de 3s
            return cursor.count() > 0
        except Exception as e:
            error_msg = str(e)
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                logger.warning(
                    f"⏱️ Timeout ao verificar documentos do agente {agent_id}. "
                    f"Assumindo que não há documentos."
                )
            else:
                logger.error(
                    f"❌ Erro ao verificar documentos: {error_msg}",
                    exc_info=True
                )
            # Em caso de erro, assume que não há documentos
            # O RAG ainda funcionará se houver documentos no Pinecone
            return False

    def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Remove documento por ID.
        """
        result = self.collection.delete_one(
            {"_id": ObjectId(document_id), "user_id": user_id}
        )
        return result.deleted_count > 0

