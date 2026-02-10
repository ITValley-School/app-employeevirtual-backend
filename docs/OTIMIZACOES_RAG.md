# ⚡ Otimizações de Performance - Sistema RAG

**Data:** 19/11/2025  
**Problema:** Agentes RAG estavam lentos devido a múltiplas inicializações do Pinecone

---

## 🔍 Problemas Identificados

### 1. **Pinecone sendo inicializado a cada requisição**
- **Sintoma:** Logs repetidos de "Discovering subpackages" e "Installing plugin inference"
- **Causa:** `AIService` sendo instanciado a cada requisição HTTP
- **Impacto:** ~2-3 segundos de overhead por requisição

### 2. **ensure_index() chamado a cada execução**
- **Sintoma:** Chamada HTTP ao Pinecone para listar índices em cada `run()`
- **Causa:** `ensure_index()` sendo chamado dentro do método `run()`
- **Impacto:** ~500ms-1s de overhead por execução

### 3. **Query usando filter ao invés de namespace**
- **Sintoma:** Queries lentas no Pinecone
- **Causa:** Usando `filter={"agent_id": {"$eq": agent_id}}` ao invés de `namespace=agent_id`
- **Impacto:** Namespace é muito mais eficiente (índice nativo)

### 4. **Index object sendo criado a cada query**
- **Sintoma:** Overhead desnecessário
- **Causa:** `pinecone.Index()` sendo chamado a cada `retrieve()`
- **Impacto:** ~100-200ms por query

### 5. **MongoDB timeouts**
- **Sintoma:** `ServerSelectionTimeoutError` nos logs
- **Causa:** Problemas de conectividade/rede com MongoDB
- **Impacto:** Lentidão em operações que dependem do MongoDB

---

## ✅ Otimizações Implementadas

### 1. **Singleton Pattern para AIService**
```python
# Antes: Nova instância a cada requisição
self.ai_service = AIService()

# Depois: Singleton reutilizado
self.ai_service = AIService.get_instance()
```

**Benefício:** Pinecone inicializado apenas uma vez na vida da aplicação

---

### 2. **ensure_index() apenas na inicialização**
```python
# Antes: Chamado a cada run()
def run(...):
    self.ensure_index()  # ❌ Lento

# Depois: Chamado apenas uma vez no __init__
def __init__(...):
    self._ensure_index_once()  # ✅ Rápido
```

**Benefício:** Elimina ~500ms-1s por execução

---

### 3. **Cache do Index Object**
```python
# Antes: Criado a cada query
index = context.deps.pinecone.Index(context.deps.index_name)  # ❌

# Depois: Cacheado e reutilizado
self._index_cache = self.pinecone_client.Index(self.index_name)  # ✅
```

**Benefício:** Elimina ~100-200ms por query

---

### 4. **Uso de Namespace ao invés de Filter**
```python
# Antes: Filter (lento)
results = index.query(
    vector=vector,
    filter={"agent_id": {"$eq": agent_id}}  # ❌
)

# Depois: Namespace (muito mais rápido)
results = index.query(
    vector=vector,
    namespace=agent_id  # ✅
)
```

**Benefício:** Queries 5-10x mais rápidas (namespace é índice nativo do Pinecone)

---

### 5. **Logging de Performance**
```python
logger.info("📊 Retrieve completo em %.3fs (embedding: %.3fs, query: %.3fs)", 
           total_time, embedding_time, query_time)
```

**Benefício:** Facilita identificar gargalos futuros

---

## 📊 Melhorias Esperadas

| Operação | Antes | Depois | Melhoria |
|----------|-------|--------|----------|
| Inicialização Pinecone | ~2-3s (a cada req) | ~2-3s (uma vez) | **100%** |
| ensure_index() | ~500ms (a cada exec) | 0ms | **100%** |
| Query Pinecone | ~500-1000ms | ~100-200ms | **70-80%** |
| **Total por execução** | **~3-4s** | **~1-2s** | **50-60%** |

---

## 🔧 Mudanças Técnicas

### Arquivos Modificados:

1. **`integrations/ai/rag_agent.py`**
   - Cache do index object
   - `ensure_index()` movido para `__init__`
   - Uso de `namespace` ao invés de `filter`
   - Logging de performance

2. **`services/ai_service.py`**
   - Singleton pattern (`get_instance()`)
   - Logging melhorado

3. **`services/agent_service.py`**
   - Usa `AIService.get_instance()`

4. **`services/chat_service.py`**
   - Usa `AIService.get_instance()`

---

## ⚠️ Observações Importantes

### MongoDB Timeouts
Os erros de timeout do MongoDB são um problema separado de infraestrutura/rede:
- Verificar conectividade com `fc-b7297e2e7154-000.global.mongocluster.cosmos.azure.com:10260`
- Considerar aumentar timeouts ou usar connection pooling
- Verificar firewall/whitelist do Azure Cosmos DB

### Pinecone SDK
O Pinecone SDK ainda faz "Discovering subpackages" na primeira inicialização, mas agora isso acontece apenas uma vez (não a cada requisição).

---

## 🧪 Como Testar

1. **Reiniciar o servidor** para aplicar as mudanças
2. **Fazer uma requisição** e verificar logs:
   ```
   🔧 Inicializando Pinecone client para índice employee
   ✅ Índice employee já existe
   ✅ RagAgentRunner inicializado com sucesso
   ```
3. **Fazer múltiplas requisições** e verificar que não há mais logs repetidos de "Discovering subpackages"
4. **Verificar performance** nos logs:
   ```
   📊 Retrieve completo em 0.234s (embedding: 0.120s, query: 0.114s)
   ✅ RAG executado em 1.456s
   ```

---

## 📝 Próximos Passos (Opcional)

1. **Connection Pooling MongoDB:** Implementar pool de conexões para reduzir timeouts
2. **Async Pinecone:** Considerar usar cliente assíncrono do Pinecone se necessário
3. **Cache de Embeddings:** Cachear embeddings de queries similares
4. **Métricas:** Adicionar métricas de performance (Prometheus/Datadog)

---

**Última atualização:** 19/11/2025

