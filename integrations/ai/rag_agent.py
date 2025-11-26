"""
Executor RAG baseado em Pydantic AI com Pinecone.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from pydantic_ai import Agent as PydanticAgent, RunContext

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RagDependencies:
    """
    Dependências compartilhadas via RunContext.
    """

    openai: OpenAI
    index: any  # Pinecone Index object (cacheado)
    agent_id: str


def _build_agent(system_prompt: str) -> PydanticAgent[RagDependencies]:
    """
    Constrói agente Pydantic com tool retrieve integrada.
    """

    agent = PydanticAgent(
        model="openai:gpt-4o-mini",
        system_prompt=system_prompt,
        deps_type=RagDependencies,
    )

    @agent.tool
    def retrieve(context: RunContext[RagDependencies], search_query: str) -> str:
        """
        Busca trechos relacionados ao agente no Pinecone usando namespace.
        """
        import time
        start_time = time.perf_counter()
        
        logger.info("🔍 Buscando contexto no namespace %s", context.deps.agent_id)
        
        # Gera embedding da query
        embedding_start = time.perf_counter()
        embedding = context.deps.openai.embeddings.create(
            input=search_query,
            model="text-embedding-3-small",
        )
        vector = embedding.data[0].embedding
        embedding_time = time.perf_counter() - embedding_start
        logger.debug("   Embedding gerado em %.3fs", embedding_time)

        # Query no Pinecone usando namespace (muito mais eficiente que filter)
        query_start = time.perf_counter()
        results = context.deps.index.query(
            vector=vector,
            top_k=8,
            include_metadata=True,
            namespace=context.deps.agent_id,  # Usa namespace ao invés de filter
        )
        query_time = time.perf_counter() - query_start
        
        match_count = len(results.matches or [])
        logger.info(
            "✅ Consulta Pinecone namespace=%s retornou %s matches em %.3fs",
            context.deps.agent_id,
            match_count,
            query_time
        )

        if not results.matches:
            logger.warning("⚠️ Nenhum match encontrado para namespace %s", context.deps.agent_id)
            return "Nenhum conhecimento relevante encontrado."

        sections = []
        for match in results.matches:
            metadata = match.metadata or {}
            title = metadata.get("title") or metadata.get("file_name") or "Conteúdo"
            content = metadata.get("content") or metadata.get("text") or ""
            sections.append(f"# {title}\n\n{content}")

        total_time = time.perf_counter() - start_time
        logger.info("📊 Retrieve completo em %.3fs (embedding: %.3fs, query: %.3fs)", 
                   total_time, embedding_time, query_time)

        return "\n\n".join(sections)

    return agent


class RagAgentRunner:
    """
    Executa prompts utilizando agente RAG integrado ao Pinecone.
    Otimizado para performance com cache de index e namespace.
    """

    def __init__(self, index_name: str):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada para RAG")
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY não configurada para RAG")

        self.index_name = index_name
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        
        # Inicializa Pinecone client uma única vez
        logger.info("🔧 Inicializando Pinecone client para índice %s", index_name)
        self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        
        # Cache do index object (evita criar a cada query)
        self._index_cache: Optional[any] = None
        self._index_ensured = False
        
        self.agent = _build_agent(
            "Você é um agente RAG. Sempre use a ferramenta retrieve quando precisar de contexto."
            " Responda em português e cite os trechos recuperados."
        )
        
        # Garante índice na inicialização (apenas uma vez)
        self._ensure_index_once()

    def _ensure_index_once(self) -> None:
        """
        Garante que o índice exista (executado apenas uma vez na inicialização).
        """
        if self._index_ensured:
            return
            
        try:
            indexes = self.pinecone_client.list_indexes()
            if hasattr(indexes, "names"):
                existing = indexes.names()
            else:
                existing = [idx["name"] for idx in indexes]
            
            if self.index_name not in existing:
                logger.info("📦 Criando índice Pinecone %s", self.index_name)
                self.pinecone_client.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=settings.pinecone_cloud,
                        region=settings.pinecone_region,
                    ),
                )
                logger.info("✅ Índice %s criado com sucesso", self.index_name)
            else:
                logger.info("✅ Índice %s já existe", self.index_name)
            
            # Cache do index object
            self._index_cache = self.pinecone_client.Index(self.index_name)
            self._index_ensured = True
        except Exception as exc:
            logger.error("❌ Erro ao garantir índice: %s", exc)
            raise

    def _get_index(self):
        """Retorna index cacheado"""
        if self._index_cache is None:
            self._index_cache = self.pinecone_client.Index(self.index_name)
        return self._index_cache

    def run(
        self,
        *,
        agent_id: str,
        agent_name: str,
        instructions: Optional[str],
        user_message: str,
    ) -> str:
        """
        Executa o agente RAG com instruções específicas.
        """
        import time
        start_time = time.perf_counter()
        
        logger.info(
            "🚀 Executando RAG para agente %s (%s) no índice %s",
            agent_id,
            agent_name,
            self.index_name,
        )

        # Usa index cacheado
        index = self._get_index()
        
        deps = RagDependencies(
            openai=self.openai_client,
            index=index,  # Passa index cacheado
            agent_id=agent_id,
        )

        instructions_block = instructions or f"Responda como o agente {agent_name}."
        prompt = (
            f"Instruções específicas:\n{instructions_block}\n\n"
            f"Pergunta do usuário:\n{user_message}"
        )

        result = self.agent.run_sync(prompt, deps=deps)
        execution_time = time.perf_counter() - start_time
        
        response_text = result.data.response if hasattr(result.data, "response") else str(result.data)
        logger.info("✅ RAG executado em %.3fs (resposta: %d chars)", 
                   execution_time, len(response_text))
        
        return response_text

