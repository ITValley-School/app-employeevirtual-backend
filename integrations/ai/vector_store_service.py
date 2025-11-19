"""Vector store integration using OpenAI embeddings and Pinecone."""
from __future__ import annotations

import io
import logging
import uuid
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader

from config.settings import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Handles PDF ingestion and namespace management in Pinecone."""

    EMBEDDING_MODEL = "text-embedding-3-small"
    DEFAULT_CHUNK_SIZE = 1500
    DEFAULT_CHUNK_OVERLAP = 200

    def __init__(self, index_name: Optional[str] = None):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada para VectorStoreService")
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY não configurada para VectorStoreService")

        self.index_name = index_name or settings.pinecone_index_name
        if not self.index_name:
            raise ValueError("PINECONE_INDEX_NAME não configurado para VectorStoreService")

        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)

        self._ensure_index()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def ensure_namespace(self, namespace: str) -> None:
        """Ensures a namespace exists by seeding a placeholder vector."""
        if not namespace:
            return

        index = self.pinecone_client.Index(self.index_name)
        stats = index.describe_index_stats()
        namespaces = stats.get("namespaces", {}) if stats else {}
        if namespace in namespaces:
            logger.info("Namespace %s já existe no índice %s", namespace, self.index_name)
            return

        logger.info("Criando namespace %s no índice %s", namespace, self.index_name)
        placeholder_text = f"Placeholder namespace para agente {namespace}"
        placeholder_vector = self._embed_texts([placeholder_text])[0]
        index.upsert(
            vectors=[
                {
                    "id": f"{namespace}-placeholder",
                    "values": placeholder_vector,
                    "metadata": {
                        "agent_id": namespace,
                        "doc_type": "placeholder",
                        "content": "Namespace inicializado",
                    },
                }
            ],
            namespace=namespace,
        )
        logger.info("Namespace %s inicializado com placeholder", namespace)

    def upsert_pdf(
        self,
        *,
        agent_id: str,
        user_id: str,
        file_name: str,
        file_content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Extracts text, chunks it, embeds and upserts into Pinecone."""
        if not file_content:
            raise ValueError("Arquivo PDF não pode estar vazio")

        text = self._extract_text(file_content)
        chunks = self._chunk_text(text)
        if not chunks:
            raise ValueError("Não foi possível extrair conteúdo válido do PDF")

        embeddings = self._embed_texts(chunks)
        vectors = []
        base_metadata = metadata.copy() if metadata else {}
        base_metadata.update({
            "agent_id": agent_id,
            "user_id": user_id,
            "file_name": file_name,
            "doc_type": "chunk",
        })

        for idx, embedding in enumerate(embeddings):
            entry_metadata = base_metadata.copy()
            entry_metadata["chunk_index"] = idx
            entry_metadata["content"] = chunks[idx]

            vectors.append(
                {
                    "id": f"{agent_id}-{uuid.uuid4()}",
                    "values": embedding,
                    "metadata": entry_metadata,
                }
            )

        index = self.pinecone_client.Index(self.index_name)
        logger.info(
            "Upserting %s chunks no namespace %s (índice %s)",
            len(vectors),
            agent_id,
            self.index_name,
        )
        index.upsert(vectors=vectors, namespace=agent_id)

        # Remove placeholder vector caso exista
        index.delete(ids=[f"{agent_id}-placeholder"], namespace=agent_id)

        return {
            "message": f"Upsert realizado com sucesso. Total de chunks inseridos: {len(vectors)}",
            "upserted_count": len(vectors),
            "namespace": agent_id,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_index(self) -> None:
        indexes = self.pinecone_client.list_indexes()
        if hasattr(indexes, "names"):
            existing = indexes.names()
        else:
            existing = [item.get("name") for item in indexes]

        if self.index_name in existing:
            return

        logger.info("Criando índice Pinecone %s", self.index_name)
        self.pinecone_client.create_index(
            name=self.index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
        )

    def _extract_text(self, content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        pages: List[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text.strip())
        return "\n".join(filter(None, pages)).strip()

    def _chunk_text(
        self,
        text: str,
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> List[str]:
        if not text:
            return []

        chunks: List[str] = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += max(chunk_size - overlap, 1)
        return chunks

    def _embed_texts(self, chunks: List[str]) -> List[List[float]]:
        response = self.openai_client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=chunks,
        )
        return [item.embedding for item in response.data]
