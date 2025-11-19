"""Quick script to validate Pinecone connectivity with current environment variables.

Usage:
    python scripts/test_pinecone_connection.py
"""
from __future__ import annotations

import sys
from pprint import pprint

from pinecone import Pinecone

# Allow running from scripts/ folder without installing package
import os
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings


def main() -> None:
    if not settings.pinecone_api_key:
        sys.exit("PINECONE_API_KEY não definido no ambiente.")
    if not settings.pinecone_index_name:
        sys.exit("PINECONE_INDEX_NAME não definido no ambiente.")

    client = Pinecone(api_key=settings.pinecone_api_key)
    print("✅ Autenticado no Pinecone")

    indexes = client.list_indexes()
    names = indexes.names() if hasattr(indexes, "names") else [idx["name"] for idx in indexes]
    print("📚 Índices disponíveis:")
    pprint(names)

    index_name = settings.pinecone_index_name
    if index_name not in names:
        print(f"⚠️ Índice '{index_name}' não encontrado. Será criado se o backend subir com VectorStoreService.")
        return

    index = client.Index(index_name)
    stats = index.describe_index_stats()
    print(f"ℹ️ Stats do índice '{index_name}':")
    pprint(stats)

    namespace = input("Digite um namespace (agent_id) para conferir, ou deixe vazio para pular: ").strip()
    if namespace:
        ns_stats = stats.get("namespaces", {}).get(namespace)
        if ns_stats:
            print(f"✅ Namespace '{namespace}' contém {ns_stats.get('vector_count', 0)} vetores.")
        else:
            print(f"⚠️ Namespace '{namespace}' não possui vetores ou não existe.")

if __name__ == "__main__":
    main()
