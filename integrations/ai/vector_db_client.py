"""
Cliente HTTP para enviar PDFs e metadados ao serviço de Vector DB (Pinecone).
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

import requests

from config.settings import settings

logger = logging.getLogger(__name__)


class VectorDBClient:
    """
    Cliente responsável por enviar documentos em PDF e metadados
    para o microserviço externo que realiza o upsert no banco vetorial.
    """

    def __init__(self, base_url: Optional[str] = None, index_name: Optional[str] = None, timeout: int = 120):
        self.base_url = (base_url or settings.vector_db_base_url).rstrip("/")
        self.index_name = index_name or settings.vector_db_index_name
        self.timeout = timeout

    def upload_pdf(
        self,
        file_name: str,
        content: bytes,
        content_type: Optional[str],
        namespace: str,
        metadata_json: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia PDF e metadados para o serviço externo.
        
        Args:
            file_name: Nome do arquivo PDF
            content: Conteúdo binário do PDF
            content_type: Tipo MIME do arquivo
            namespace: Namespace do Pinecone (geralmente agent_id)
            metadata_json: JSON string com metadados opcionais
            
        Returns:
            Dict com resposta do microserviço
        """
        files = {
            "filepdf": (
                file_name,
                content,
                content_type or "application/pdf",
            )
        }

        # Sempre envia index_name e namespace
        data: Dict[str, Any] = {
            "index_name": self.index_name,
            "namespace": namespace,
        }
        
        # Se houver metadados, usa endpoint com metadonnes
        if metadata_json:
            data["metadone"] = metadata_json
            endpoint = f"{self.base_url}/upsert/upsert-pdf/metadonnes"
        else:
            endpoint = f"{self.base_url}/upsert/upsert-pdf"

        logger.info(
            "Enviando PDF para Vector DB: endpoint=%s, index=%s, namespace=%s",
            endpoint,
            self.index_name,
            namespace
        )

        response = requests.post(
            endpoint,
            files=files,
            data=data,
            timeout=self.timeout,
        )
        response.raise_for_status()

        try:
            return response.json()
        except ValueError as exc:
            logger.error("Resposta do Vector DB não está em JSON válido: %s", exc)
            raise ValueError("Resposta do serviço vetorial inválida") from exc

    def delete_document(
        self,
        namespace: str,
        file_name: Optional[str] = None,
        delete_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Remove documentos do Pinecone via microserviço externo.
        
        Args:
            namespace: Namespace do Pinecone (geralmente agent_id)
            file_name: Nome do arquivo específico a deletar (opcional)
            delete_all: Se True, deleta todos os documentos do namespace
            
        Returns:
            Dict com resposta do microserviço
            
        Note:
            O microserviço pode ter diferentes endpoints:
            - DELETE /delete/namespace/{namespace} - deleta todo o namespace
            - DELETE /delete/document/{namespace}/{file_name} - deleta documento específico
        """
        data: Dict[str, Any] = {
            "index_name": self.index_name,
            "namespace": namespace,
        }
        
        if delete_all:
            endpoint = f"{self.base_url}/delete/namespace/{namespace}"
            logger.info(
                "Deletando todos os documentos do namespace: index=%s, namespace=%s",
                self.index_name,
                namespace
            )
        elif file_name:
            endpoint = f"{self.base_url}/delete/document/{namespace}/{file_name}"
            data["file_name"] = file_name
            logger.info(
                "Deletando documento específico: index=%s, namespace=%s, file=%s",
                self.index_name,
                namespace,
                file_name
            )
        else:
            raise ValueError("Deve fornecer file_name ou definir delete_all=True")
        
        response = requests.delete(
            endpoint,
            json=data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        
        try:
            return response.json()
        except ValueError:
            # Alguns endpoints podem retornar apenas status 200 sem JSON
            return {"success": True, "message": "Documento(s) deletado(s) com sucesso"}

