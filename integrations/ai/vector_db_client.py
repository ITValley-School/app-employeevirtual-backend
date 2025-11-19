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

    def __init__(self, base_url: Optional[str] = None, timeout: int = 120):
        self.base_url = (base_url or settings.vector_db_base_url).rstrip("/")
        self.timeout = timeout

    @property
    def upload_endpoint(self) -> str:
        return f"{self.base_url}/upsert/upsert-pdf/metadonnes"

    def upload_pdf(
        self,
        file_name: str,
        content: bytes,
        content_type: Optional[str],
        metadata_json: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia PDF e metadados para o serviço externo.
        """
        files = {
            "filepdf": (
                file_name,
                content,
                content_type or "application/pdf",
            )
        }

        data: Dict[str, Any] = {}
        if metadata_json:
            data["metadone"] = metadata_json

        logger.info("Enviando PDF para Vector DB em %s", self.upload_endpoint)

        response = requests.post(
            self.upload_endpoint,
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

