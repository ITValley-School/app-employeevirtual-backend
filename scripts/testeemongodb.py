#!/usr/bin/env python3
"""
Script para testar conexão e funcionalidades do MongoDB
"""
import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb import (
    get_mongo_client, get_async_mongo_client,
    get_database, get_async_database,
    Collections, create_indexes, test_mongodb_connection,
    create_chat_conversation, add_messages_to_conversation,
    get_conversation_history, update_conversation_context,
    close_mongo_connections
)

class MongoDBTester:
    """Classe para testar funcionalidades do MongoDB"""
    
    def __init__(self):
        self.sync_client = None
        self.async_client = None
        self.sync_db = None
        self.async_db = None
        
    def print_separator(self, title: str):
        """Imprime um separador visual"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Imprime mensagem informativa"""
        print(f"ℹ️ {message}")
    
    def test_sync_connection(self) -> bool:
        """Testa conexão síncrona com MongoDB"""
        try:
            self.print_separator("TESTE DE CONEXÃO SÍNCRONA")
            
            # Obter cliente síncrono
            self.sync_client = get_mongo_client()
            self.print_success("Cliente MongoDB síncrono obtido")
            
            # Obter database
            self.sync_db = get_database()
            self.print_success("Database MongoDB síncrono obtido")
            
            # Testar ping
            result = self.sync_client.admin.command('ping')
            self.print_success(f"Ping bem-sucedido: {result}")
            
            # Obter informações do servidor
            server_info = self.sync_client.server_info()
            self.print_info(f"Versão do servidor: {server_info.get('version')}")
            self.print_info(f"Database: {self.sync_db.name}")
            
            # Listar collections
            collections = self.sync_db.list_collection_names()
            self.print_info(f"Collections encontradas: {len(collections)}")
            for collection in collections[:5]:  # Mostrar apenas as primeiras 5
                self.print_info(f"  - {collection}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro na conexão síncrona: {str(e)}")
            return False
    
    async def test_async_connection(self) -> bool:
        """Testa conexão assíncrona com MongoDB"""
        try:
            self.print_separator("TESTE DE CONEXÃO ASSÍNCRONA")
            
            # Obter cliente assíncrono
            self.async_client = get_async_mongo_client()
            self.print_success("Cliente MongoDB assíncrono obtido")
            
            # Obter database
            self.async_db = get_async_database()
            self.print_success("Database MongoDB assíncrono obtido")
            
            # Testar ping
            result = await self.async_db.command('ping')
            self.print_success(f"Ping assíncrono bem-sucedido: {result}")
            
            # Testar conexão completa
            connection_info = await test_mongodb_connection()
            if connection_info["connected"]:
                self.print_success("Teste de conexão assíncrona completo")
                self.print_info(f"Versão: {connection_info.get('server_version')}")
                self.print_info(f"Collections: {connection_info.get('collections_count')}")
            else:
                self.print_error(f"Falha no teste de conexão: {connection_info.get('error')}")
                return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro na conexão assíncrona: {str(e)}")
            return False
    
    async def test_collections(self) -> bool:
        """Testa criação e acesso às collections"""
        try:
            self.print_separator("TESTE DE COLLECTIONS")
            
            # Testar collections definidas
            collections_to_test = [
                Collections.CHAT_CONVERSATIONS,
                Collections.USER_ACTIVITIES,
                Collections.SYSTEM_LOGS,
                Collections.TEMP_FILES
            ]
            
            for collection_name in collections_to_test:
                try:
                    collection = self.async_db[collection_name]
                    
                    # Testar inserção de documento de teste
                    test_doc = {
                        "test": True,
                        "timestamp": datetime.utcnow(),
                        "script": "mongodb_test"
                    }
                    
                    result = await collection.insert_one(test_doc)
                    self.print_success(f"Collection {collection_name}: documento inserido (ID: {result.inserted_id})")
                    
                    # Testar busca
                    found_doc = await collection.find_one({"_id": result.inserted_id})
                    if found_doc:
                        self.print_success(f"Collection {collection_name}: documento encontrado")
                    
                    # Limpar documento de teste
                    await collection.delete_one({"_id": result.inserted_id})
                    self.print_info(f"Collection {collection_name}: documento de teste removido")
                    
                except Exception as e:
                    self.print_error(f"Erro na collection {collection_name}: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro no teste de collections: {str(e)}")
            return False
    
    async def test_chat_functionality(self) -> bool:
        """Testa funcionalidades específicas de chat"""
        try:
            self.print_separator("TESTE DE FUNCIONALIDADES DE CHAT")
            
            # Dados de teste
            test_conversation = {
                "conversation_id": "test-conv-123",
                "user_id": "test-user-456",
                "agent_id": "test-agent-789",
                "title": "Teste de Conversa MongoDB",
                "context": {"test": True}
            }
            
            # Testar criação de conversa
            conv_id = await create_chat_conversation(test_conversation)
            self.print_success(f"Conversa criada: {conv_id}")
            
            # Testar adição de mensagens
            test_messages = [
                {
                    "id": "msg-1",
                    "content": "Olá, como você pode me ajudar?",
                    "message_type": "user",
                    "user_id": "test-user-456",
                    "metadata": {"test": True}
                },
                {
                    "id": "msg-2", 
                    "content": "Olá! Sou seu assistente virtual. Como posso ajudar?",
                    "message_type": "agent",
                    "agent_id": "test-agent-789",
                    "metadata": {"test": True, "model": "gpt-4o-mini"}
                }
            ]
            
            success = await add_messages_to_conversation(conv_id, test_messages)
            if success:
                self.print_success("Mensagens adicionadas com sucesso")
            else:
                self.print_error("Falha ao adicionar mensagens")
                return False
            
            # Testar busca de histórico
            history = await get_conversation_history(conv_id, limit=10)
            if history:
                self.print_success(f"Histórico obtido: {len(history['messages'])} mensagens")
                for msg in history['messages']:
                    self.print_info(f"  - [{msg['message_type']}] {msg['content'][:50]}...")
            else:
                self.print_error("Falha ao obter histórico")
                return False
            
            # Testar atualização de contexto
            new_context = {"updated": True, "timestamp": datetime.utcnow()}
            context_updated = await update_conversation_context(conv_id, new_context)
            if context_updated:
                self.print_success("Contexto atualizado com sucesso")
            else:
                self.print_error("Falha ao atualizar contexto")
            
            # Limpar dados de teste
            await self.async_db[Collections.CHAT_CONVERSATIONS].delete_one({"_id": conv_id})
            self.print_info("Dados de teste removidos")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro no teste de chat: {str(e)}")
            return False
    
    async def test_indexes(self) -> bool:
        """Testa criação de índices"""
        try:
            self.print_separator("TESTE DE ÍNDICES")
            
            # Criar índices
            await create_indexes()
            self.print_success("Índices criados com sucesso")
            
            # Verificar alguns índices específicos
            collections_to_check = [
                Collections.CHAT_CONVERSATIONS,
                Collections.USER_ACTIVITIES,
                Collections.SYSTEM_LOGS
            ]
            
            for collection_name in collections_to_check:
                try:
                    collection = self.async_db[collection_name]
                    indexes = await collection.list_indexes().to_list(length=None)
                    self.print_info(f"Collection {collection_name}: {len(indexes)} índices")
                    
                    for index in indexes[:3]:  # Mostrar apenas os primeiros 3
                        self.print_info(f"  - {index['name']}")
                        
                except Exception as e:
                    self.print_error(f"Erro ao verificar índices de {collection_name}: {str(e)}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro no teste de índices: {str(e)}")
            return False
    
    async def test_performance(self) -> bool:
        """Testa performance básica"""
        try:
            self.print_separator("TESTE DE PERFORMANCE")
            
            # Teste de inserção em lote
            collection = self.async_db[Collections.TEMP_FILES]
            
            # Preparar documentos de teste
            test_docs = []
            for i in range(100):
                test_docs.append({
                    "test_id": f"perf-test-{i}",
                    "data": f"Test data {i}",
                    "timestamp": datetime.utcnow(),
                    "index": i
                })
            
            # Inserção em lote
            start_time = datetime.utcnow()
            result = await collection.insert_many(test_docs)
            end_time = datetime.utcnow()
            
            insert_time = (end_time - start_time).total_seconds()
            self.print_success(f"Inserção em lote: {len(result.inserted_ids)} documentos em {insert_time:.3f}s")
            
            # Teste de busca
            start_time = datetime.utcnow()
            found_docs = await collection.find({"test_id": {"$regex": "perf-test-"}}).to_list(length=None)
            end_time = datetime.utcnow()
            
            search_time = (end_time - start_time).total_seconds()
            self.print_success(f"Busca: {len(found_docs)} documentos em {search_time:.3f}s")
            
            # Limpar dados de teste
            await collection.delete_many({"test_id": {"$regex": "perf-test-"}})
            self.print_info("Dados de teste de performance removidos")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro no teste de performance: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES DO MONGODB")
        print("=" * 60)
        
        tests = [
            ("Conexão Síncrona", self.test_sync_connection),
            ("Conexão Assíncrona", self.test_async_connection),
            ("Collections", self.test_collections),
            ("Funcionalidades de Chat", self.test_chat_functionality),
            ("Índices", self.test_indexes),
            ("Performance", self.test_performance)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                results.append((test_name, result))
            except Exception as e:
                self.print_error(f"Erro no teste {test_name}: {str(e)}")
                results.append((test_name, False))
        
        # Resumo dos resultados
        self.print_separator("RESUMO DOS TESTES")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            if result:
                self.print_success(f"{test_name}: PASSOU")
                passed += 1
            else:
                self.print_error(f"{test_name}: FALHOU")
        
        print(f"\n�� RESULTADO FINAL: {passed}/{total} testes passaram")
        
        if passed == total:
            self.print_success("🎉 TODOS OS TESTES PASSARAM! MongoDB está funcionando perfeitamente.")
        else:
            self.print_error(f"⚠️ {total - passed} teste(s) falharam. Verifique a configuração do MongoDB.")
        
        # Fechar conexões
        try:
            await close_mongo_connections()
            self.print_info("Conexões MongoDB fechadas")
        except Exception as e:
            self.print_error(f"Erro ao fechar conexões: {str(e)}")

async def main():
    """Função principal"""
    tester = MongoDBTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    # Executar testes
    asyncio.run(main())