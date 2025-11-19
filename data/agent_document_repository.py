"""
Repositório MongoDB para documentos vetoriais de agentes.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from data.mongodb import get_database, Collections


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
        """
        document = {
            "agent_id": agent_id,
            "user_id": user_id,
            "file_name": file_name,
            "metadata": metadata or {},
            "vector_response": vector_response or {},
            "created_at": datetime.utcnow(),
        }
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return _stringify_id(document.copy())

    def list_documents(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Lista documentos associados a um agente do usuário.
        """
        docs = self.collection.find(
            {"agent_id": agent_id, "user_id": user_id}
        ).sort("created_at", -1)
        return [_stringify_id(doc) for doc in docs]

    def has_documents(self, agent_id: str) -> bool:
        """
        Verifica se o agente possui documentos vetoriais.
        """
        return self.collection.count_documents({"agent_id": agent_id}) > 0

    def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Remove documento por ID.
        """
        result = self.collection.delete_one(
            {"_id": ObjectId(document_id), "user_id": user_id}
        )
        return result.deleted_count > 0

