# 📊 Análise: Execução do Agente de IA

**Data:** 25/11/2025  
**Objetivo:** Analisar o fluxo completo de execução do agente de IA criado pelo usuário

---

## 🗂️ Collections MongoDB Identificadas

1. **`agent_documents`** - Documentos PDF associados aos agentes
2. **`chat_conversations`** - Conversas/sessões de chat
3. **`chat_messages`** - Mensagens individuais (backup/legado)

---

## 🔄 Fluxo Completo de Execução

### 1️⃣ **Criação do Agente**

**Endpoint:** `POST /api/agents/`

**Fluxo:**
```
User → API → AgentService.create_agent() → AgentFactory → AgentEntity → AgentRepository → Azure SQL
```

**O que é salvo:**
- ✅ **Azure SQL** (`agents` table): Configuração do agente (nome, instruções, modelo, temperatura, etc.)
- ❌ **MongoDB**: Nada é salvo na criação

**Dados persistidos:**
- `id`, `user_id`, `name`, `description`, `agent_type`, `system_prompt`
- `llm_provider`, `model`, `temperature`, `max_tokens`
- `status`, `created_at`, `updated_at`, `last_used`, `usage_count`

---

### 2️⃣ **Upload de Documentos (RAG)**

**Endpoint:** `POST /api/agents/{agent_id}/documents`

**Fluxo:**
```
User → API → AgentService.upload_agent_document()
  ├─→ VectorDBClient.upload_pdf() → Microserviço → Pinecone (namespace=agent_id)
  └─→ AgentDocumentRepository.record_upload() → MongoDB (agent_documents)
```

**O que é salvo:**
- ✅ **Pinecone**: PDF processado, chunked, embedded e upserted no namespace do agente
- ✅ **MongoDB** (`agent_documents`): Metadados do upload
  ```json
  {
    "agent_id": "uuid",
    "user_id": "uuid",
    "file_name": "documento.pdf",
    "metadata": {...},
    "vector_response": {...},
    "created_at": "2025-11-25T..."
  }
  ```

**⚠️ Tratamento de Erros:**
- Se MongoDB falhar (timeout), o documento ainda está no Pinecone
- Retorna sucesso parcial com aviso (`mongo_error: true`)

---

### 3️⃣ **Execução do Agente**

**Endpoint:** `POST /api/agents/{agent_id}/execute`

**Fluxo Detalhado:**

```
1. AgentService.execute_agent()
   ├─ Busca agente no Azure SQL
   ├─ Verifica se tem documentos: AgentDocumentRepository.has_documents(agent_id)
   │  └─ Query MongoDB: agent_documents.find({"agent_id": agent_id}).limit(1)
   │
   ├─ Decisão RAG:
   │  ├─ supports_rag = bool(PINECONE_API_KEY && INDEX_NAME)
   │  └─ has_docs = MongoDB query result
   │
   ├─ Execução:
   │  ├─ COM RAG (se supports_rag && has_docs):
   │  │  └─ AIService.generate_rag_response_sync()
   │  │     └─ RagAgentRunner.run()
   │  │        ├─ Gera embedding da query (OpenAI)
   │  │        ├─ Query Pinecone (namespace=agent_id, top_k=8)
   │  │        ├─ Formata contexto recuperado
   │  │        └─ Executa PydanticAI Agent com tool retrieve()
   │  │
   │  └─ SEM RAG (fallback):
   │     └─ AIService.generate_response_sync()
   │        └─ PydanticAI Agent direto (sem RAG)
   │
   ├─ Atualiza agente no Azure SQL:
   │  ├─ last_used = now
   │  ├─ usage_count += 1
   │  └─ updated_at = now
   │
   └─ Retorna resposta
```

**O que é salvo:**
- ✅ **Azure SQL**: Atualiza `last_used`, `usage_count`, `updated_at`
- ✅ **MongoDB** (assíncrono, não bloqueante): Salva conversa em background se tiver `session_id`

**✅ Solução Implementada:**
- A execução via `/api/agents/{agent_id}/execute` **agora persiste** a conversa no MongoDB
- Persistência é **assíncrona** (thread separada) - **não bloqueia** a resposta ao frontend
- Se MongoDB estiver lento/indisponível, não afeta o tempo de resposta

---

### 4️⃣ **Execução via Chat (Sessão)**

**Endpoint:** `POST /api/chat/sessions/{session_id}/messages`

**Fluxo:**
```
User → API → ChatService.send_message_async()
  ├─ Busca sessão no Azure SQL
  ├─ Cria mensagem do usuário via ChatFactory
  ├─ Salva mensagem no MongoDB (chat_conversations)
  ├─ Busca agente da sessão
  ├─ Gera resposta via AIService
  └─ Salva resposta no MongoDB (chat_conversations)
```

**O que é salvo:**
- ✅ **Azure SQL**: Sessão de chat (`chat_sessions`)
- ✅ **MongoDB** (`chat_conversations`): 
  ```json
  {
    "_id": "session_id",
    "conversation_id": "session_id",
    "user_id": "uuid",
    "agent_id": "uuid",
    "title": "Conversa - ...",
    "messages": [
      {
        "_id": ObjectId(),
        "message": "texto",
        "sender": "user|assistant",
        "context": {},
        "metadata": {},
        "created_at": "..."
      }
    ],
    "metadata": {
      "created_at": "...",
      "last_activity": "...",
      "message_count": 2,
      "status": "active"
    }
  }
  ```

---

## 🔍 Análise Crítica

### ✅ **Pontos Fortes**

1. **Separação de Responsabilidades**
   - Azure SQL para dados relacionais (agentes, sessões)
   - MongoDB para dados não-relacionais (conversas, documentos)
   - Pinecone para vetores (RAG)

2. **Tratamento de Erros Robusto**
   - MongoDB timeouts não quebram o fluxo
   - Fallback gracioso quando MongoDB está indisponível
   - Documentos no Pinecone são priorizados sobre MongoDB

3. **Performance Otimizada**
   - Singleton pattern no AIService (evita múltiplas inicializações)
   - Cache do Pinecone Index
   - Namespace no Pinecone (mais eficiente que filter)

### ⚠️ **Problemas Identificados**

#### 1. ~~**Inconsistência na Persistência**~~ ✅ **RESOLVIDO**

**✅ Solução Implementada:**
- Execução direta (`/api/agents/{agent_id}/execute`) **agora salva** no MongoDB
- Persistência é **assíncrona** (thread separada) - **não bloqueia** resposta
- Se tiver `session_id`, salva automaticamente em background

**Implementação:**
```python
# Em AgentService.execute_agent(), após gerar resposta:
if dto.session_id:
    # Salva no MongoDB de forma assíncrona (não bloqueante)
    self._save_conversation_async(
        session_id=dto.session_id,
        user_id=user_id,
        agent_id=agent.id,
        user_message=dto.message,
        assistant_message=response_text
    )

def _save_conversation_async(...):
    """Salva em thread separada - não bloqueia resposta"""
    thread = threading.Thread(target=save_in_background, daemon=True)
    thread.start()
```

**Benefícios:**
- ✅ Resposta rápida ao frontend (não espera MongoDB)
- ✅ Histórico completo de conversas
- ✅ Se MongoDB falhar, não afeta a resposta
- ✅ Fluxo simplificado e consistente

#### 2. **Verificação de Documentos Depende do MongoDB**

**Problema:**
- `has_documents()` consulta MongoDB
- Se MongoDB estiver lento/indisponível, pode retornar `False` mesmo tendo documentos no Pinecone

**Impacto:**
- RAG pode não ser usado mesmo tendo documentos no Pinecone
- Usuário pode ter enviado PDF mas o sistema não detecta

**Solução Sugerida:**
```python
def has_documents(self, agent_id: str) -> bool:
    """
    Verifica se há documentos no Pinecone (fonte da verdade).
    MongoDB é apenas cache/metadados.
    """
    try:
        # Tenta verificar no MongoDB primeiro (rápido)
        if self._check_mongodb(agent_id):
            return True
    except:
        pass
    
    # Se MongoDB falhar, verifica diretamente no Pinecone
    try:
        index = self._get_pinecone_index()
        stats = index.describe_index_stats()
        namespaces = stats.get('namespaces', {})
        return agent_id in namespaces and namespaces[agent_id].get('vector_count', 0) > 0
    except:
        return False
```

#### 3. **Collection `chat_messages` Não Utilizada**

**Problema:**
- Existe collection `chat_messages` no MongoDB mas não é usada
- Tudo é salvo em `chat_conversations` como array de mensagens

**Impacto:**
- Confusão sobre qual collection usar
- Possível inconsistência futura

**Solução:**
- Documentar que `chat_messages` é legado/backup
- Ou migrar para usar `chat_messages` como collection separada

---

## 📋 Checklist de Verificação

### Para cada execução de agente, verificar:

- [ ] Agente existe no Azure SQL?
- [ ] Agente tem documentos no MongoDB (`agent_documents`)?
- [ ] Documentos estão no Pinecone (namespace=agent_id)?
- [ ] RAG está habilitado (`supports_rag=True`)?
- [ ] Resposta foi gerada com sucesso?
- [ ] Conversa foi salva no MongoDB (se tiver `session_id`)?
- [ ] `last_used` e `usage_count` foram atualizados?

---

## 🎯 Recomendações

### 1. ~~**Unificar Persistência de Conversas**~~ ✅ **IMPLEMENTADO**

✅ Sempre salvar no MongoDB quando houver `session_id`, independente do endpoint usado.
✅ Implementado de forma assíncrona para não bloquear resposta.

### 2. **Melhorar Verificação de Documentos**

Consultar Pinecone diretamente como fallback quando MongoDB falhar.

### 3. **Adicionar Métricas**

- Tempo de resposta por tipo (RAG vs padrão)
- Taxa de uso de RAG vs fallback
- Erros de MongoDB vs sucessos

### 4. **Documentar Collections**

Criar documentação clara sobre:
- Quando usar cada collection
- Estrutura de dados esperada
- Índices necessários

---

## 📊 Estrutura de Dados MongoDB

### `agent_documents`
```json
{
  "_id": ObjectId,
  "agent_id": "uuid",
  "user_id": "uuid",
  "file_name": "documento.pdf",
  "metadata": {
    "agent_name": "...",
    ...
  },
  "vector_response": {
    "status": "...",
    ...
  },
  "created_at": ISODate
}
```

### `chat_conversations`
```json
{
  "_id": "session_id",
  "conversation_id": "session_id",
  "user_id": "uuid",
  "agent_id": "uuid",
  "title": "Conversa - ...",
  "messages": [
    {
      "_id": ObjectId,
      "message": "texto",
      "sender": "user|assistant",
      "context": {},
      "metadata": {},
      "created_at": ISODate
    }
  ],
  "metadata": {
    "created_at": ISODate,
    "last_activity": ISODate,
    "message_count": 0,
    "status": "active",
    "total_tokens": 0,
    "total_cost": 0.0
  }
}
```

---

## 🔗 Fluxograma Visual

```
┌─────────────────┐
│  User cria      │
│  Agente         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Azure SQL      │
│  (agents table) │
└─────────────────┘

┌─────────────────┐
│  User uploada   │
│  PDF            │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│Pinecone│ │ MongoDB   │
│(vectors)│ │(metadata)│
└────────┘ └──────────┘

┌─────────────────┐
│  User executa   │
│  Agente         │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│  RAG?   │ │  Padrão  │
│  (SIM)  │ │  (NÃO)   │
└────┬────┘ └────┬─────┘
     │           │
     ▼           ▼
┌─────────────────────┐
│  Pinecone Query     │
│  (namespace=agent)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  OpenAI + Pydantic  │
│  AI Agent           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Resposta Gerada    │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌──────────┐
│Azure SQL│  │ MongoDB  │
│(stats) │  │(history) │
└────────┘   └──────────┘
```

---

**Próximos Passos:**
1. Implementar persistência unificada
2. Melhorar verificação de documentos
3. Adicionar métricas e monitoramento
4. Documentar collections MongoDB

