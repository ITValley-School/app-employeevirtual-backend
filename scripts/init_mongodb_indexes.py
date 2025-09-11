#!/usr/bin/env python3
"""
Script para inicializar índices MongoDB para o sistema EmployeeVirtual
"""
import asyncio
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb import create_mongodb_indexes, get_async_database
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Função principal para inicializar índices"""
    try:
        logger.info("🚀 Iniciando criação de índices MongoDB...")
        
        # Criar índices
        await create_mongodb_indexes()
        
        logger.info("✅ Índices MongoDB criados com sucesso!")
        
        # Verificar conexão
        db = get_async_database()
        collections = await db.list_collection_names()
        logger.info(f"📊 Collections disponíveis: {collections}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar índices: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())