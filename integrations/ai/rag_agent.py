"""
Executor RAG baseado em Pydantic AI com Pinecone.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from pydantic_ai import Agent as PydanticAgent, RunContext

from config.settings import settings


@dataclass
class RagDependencies:
    """
    Dependências compartilhadas via RunContext.
    """

    openai: OpenAI
    pinecone: Pinecone
    index_name: str
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
        Busca trechos relacionados ao agente no Pinecone.
        """

        embedding = context.deps.openai.embeddings.create(
            input=search_query,
            model="text-embedding-3-small",
        )
        vector = embedding.data[0].embedding

        index = context.deps.pinecone.Index(context.deps.index_name)
        results = index.query(
            vector=vector,
            top_k=8,
            include_metadata=True,
            filter={"agent_id": {"$eq": context.deps.agent_id}},
        )

        if not results.matches:
            return "Nenhum conhecimento relevante encontrado."

        sections = []
        for match in results.matches:
            metadata = match.metadata or {}
            title = metadata.get("title") or "Conteúdo"
            url = metadata.get("url") or metadata.get("source", "")
            content = metadata.get("content") or metadata.get("text") or ""
            sections.append(f"# {title}\nURL: {url}\n\n{content}")

        return "\n\n".join(sections)

    return agent


class RagAgentRunner:
    """
    Executa prompts utilizando agente RAG integrado ao Pinecone.
    """

    def __init__(self, index_name: str):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada para RAG")
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY não configurada para RAG")

        self.index_name = index_name
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        self.agent = _build_agent(
            "Você é um agente RAG. Sempre use a ferramenta retrieve quando precisar de contexto."
            " Responda em português e cite os trechos recuperados."
        )

    def ensure_index(self) -> None:
        """
        Garante que o índice exista (idempotente).
        """
        indexes = self.pinecone_client.list_indexes()
        if hasattr(indexes, "names"):
            existing = indexes.names()
        else:
            existing = [idx["name"] for idx in indexes]
        if self.index_name not in existing:
            self.pinecone_client.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.pinecone_cloud,
                    region=settings.pinecone_region,
                ),
            )

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
        self.ensure_index()

        deps = RagDependencies(
            openai=self.openai_client,
            pinecone=self.pinecone_client,
            index_name=self.index_name,
            agent_id=agent_id,
        )

        instructions_block = instructions or f"Responda como o agente {agent_name}."
        prompt = (
            f"Instruções específicas:\n{instructions_block}\n\n"
            f"Pergunta do usuário:\n{user_message}"
        )

        result = self.agent.run_sync(prompt, deps=deps)
        return result.data.response if hasattr(result.data, "response") else str(result.data)

