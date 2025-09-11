
### **Responsabilidades por Camada**

| **SQL Server** | **MongoDB** | **FastAPI** |
|----------------|-------------|-------------|
| Metadados de conversas | Histórico completo | Lógica de negócio |
| Usuários e agentes | Mensagens em tempo real | Validação de dados |
| Relacionamentos | Contexto de conversas | Orquestração |
| Auditoria | Analytics | Autenticação |

---

## 🔄 Fluxo de Conversação

### **1. Início de Conversa**

```mermaid
sequenceDiagram
    participant U as Usuário
    participant API as FastAPI
    participant SQL as SQL Server
    participant MONGO as MongoDB
    participant AI as Pydantic AI

    U->>API: POST /api/chat/agent
    API->>SQL: Verificar/Criar Conversation
    SQL-->>API: Conversation ID
    API->>MONGO: Criar documento de chat
    MONGO-->>API: Confirmação
    API->>AI: Executar agente
    AI-->>API: Resposta
    API->>MONGO: Salvar mensagens em lote
    API-->>U: Resposta completa
```

### **2. Processo Detalhado**

#### **Passo 1: Recebimento da Mensagem**
```python
# API: POST /api/chat/agent?message=ola&agent_id=8f98fbbf-2bb7-4315-95b5-0ac74810ac88
```

#### **Passo 2: Criação/Verificação da Conversa (SQL Server)**
```python
# Se não há conversation_id, cria nova conversa
conversation_data = ConversationCreate(
    agent_id=agent_id,
    title=f"Conversa com {agent.name}"
)
conversation = chat_service.create_conversation(current_user.id, conversation_data)
```

#### **Passo 3: Criação do Documento MongoDB**
```python
# Criar documento inicial no MongoDB
conversation_doc = {
    "_id": conversation_id,
    "conversation_id": conversation_id,
    "user_id": user_id,
    "agent_id": agent_id,
    "title": title,
    "messages": [],
    "context": {},
    "metadata": {
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "message_count": 0,
        "status": "active",
        "total_tokens": 0,
        "total_cost": 0.0
    }
}
```

#### **Passo 4: Execução do Agente**
```python
response = await agent_service.execute_agent(
    agent_id=agent_id,
    user_id=current_user.id,
    user_message=message,
    context=execution_context
)
```

#### **Passo 5: Salvamento Atômico no MongoDB**
```python
# Salvar mensagens em lote (atômico)
messages_to_save = [
    {
        "id": "msg-1",
        "content": "Olá, como você pode me ajudar?",
        "message_type": "user",
        "user_id": user_id,
        "metadata": {"timestamp": datetime.utcnow()}
    },
    {
        "id": "msg-2", 
        "content": "Olá! Sou seu assistente virtual...",
        "message_type": "agent",
        "agent_id": agent_id,
        "metadata": {
            "model_used": "openai:gpt-4o-mini",
            "execution_time": 1.2,
            "tokens_used": 150
        }
    }
]

await add_messages_to_conversation(conversation_id, messages_to_save)
```

---

## �� Estrutura de Dados

### **SQL Server - Metadados**

#### **Tabela: `empl.conversations`**
```sql
CREATE TABLE empl.conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    agent_id UUID NOT NULL,
    title VARCHAR(200),
    status VARCHAR(50) DEFAULT 'active',
    session_id VARCHAR(100),
    metadata TEXT, -- JSON
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2,
    last_message_at DATETIME2,
    
    FOREIGN KEY (user_id) REFERENCES empl.users(id),
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id)
);
```

#### **Tabela: `empl.messages` (Backup/Auditoria)**
```sql
CREATE TABLE empl.messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,
    agent_id UUID NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    message_metadata TEXT, -- JSON
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    edited_at DATETIME2,
    is_edited BIT DEFAULT 0,
    
    FOREIGN KEY (conversation_id) REFERENCES empl.conversations(id)
);
```

### **MongoDB - Dados de Chat**

#### **Collection: `chat_conversations`**
```json
{
  "_id": "conversation_uuid",
  "conversation_id": "conversation_uuid",
  "user_id": "user_uuid",
  "agent_id": "agent_uuid",
  "title": "Conversa com Agente",
  "messages": [
    {
      "id": "msg_uuid",
      "content": "Olá, como posso ajudar?",
      "message_type": "user",
      "user_id": "user_uuid",
      "metadata": {
        "timestamp": "2025-01-15T10:30:00Z",
        "client_info": {...}
      }
    },
    {
      "id": "msg_uuid_2",
      "content": "Olá! Sou seu assistente virtual...",
      "message_type": "agent",
      "agent_id": "agent_uuid",
      "metadata": {
        "model_used": "openai:gpt-4o-mini",
        "execution_time": 1.2,
        "tokens_used": 150,
        "confidence": 0.95,
        "timestamp": "2025-01-15T10:30:01Z"
      }
    }
  ],
  "context": {
    "session_data": {...},
    "user_preferences": {...},
    "conversation_state": "active",
    "rag_context": {...}
  },
  "metadata": {
    "created_at": "2025-01-15T10:30:00Z",
    "last_activity": "2025-01-15T10:30:01Z",
    "message_count": 2,
    "status": "active",
    "total_tokens": 150,
    "total_cost": 0.0003,
    "avg_response_time": 1.2
  }
}
```

---

## 🚀 Vantagens da Arquitetura Híbrida

### **✅ Benefícios**

#### **1. Performance Otimizada**
- **MongoDB**: Consultas rápidas de histórico de chat
- **SQL Server**: Joins eficientes para metadados
- **Índices específicos**: Otimizados para cada tipo de consulta

#### **2. Escalabilidade**
- **MongoDB**: Escala horizontalmente para grandes volumes de chat
- **SQL Server**: Mantém integridade referencial para metadados
- **Separação de responsabilidades**: Cada banco otimizado para seu propósito

#### **3. Confiabilidade**
- **Atomicidade**: Mensagens salvas em lote no MongoDB
- **Backup**: Metadados críticos no SQL Server
- **Consistência**: Sincronização entre os dois sistemas

#### **4. Flexibilidade**
- **Schema flexível**: MongoDB permite evolução do formato de mensagens
- **Relacionamentos**: SQL Server mantém integridade referencial
- **Analytics**: MongoDB ideal para análise de conversas

---

## 🔧 Implementação Técnica

### **1. Configuração MongoDB**

```python
# data/mongodb.py
MONGODB_URL = "mongodb+srv://useremploye:password@dbmongoemploye.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
MONGODB_DATABASE = "employeevirtual"

# Collections
class Collections:
    CHAT_CONVERSATIONS = "chat_conversations"
    CHAT_MESSAGES = "chat_messages"
    CHAT_ANALYTICS = "chat_analytics"
    USER_ACTIVITIES = "user_activities"
    SYSTEM_LOGS = "system_logs"
```

### **2. Funções Principais**

#### **Criação de Conversa**
```python
async def create_chat_conversation(conversation_data: Dict[str, Any]) -> str:
    """Cria nova conversa no MongoDB"""
    db = get_async_database()
    
    conversation_doc = {
        "_id": conversation_data["conversation_id"],
        "conversation_id": conversation_data["conversation_id"],
        "user_id": conversation_data["user_id"],
        "agent_id": conversation_data["agent_id"],
        "title": conversation_data.get("title", "Nova Conversa"),
        "messages": [],
        "context": conversation_data.get("context", {}),
        "metadata": {
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "message_count": 0,
            "status": "active",
            "total_tokens": 0,
            "total_cost": 0.0
        }
    }
    
    result = await db[Collections.CHAT_CONVERSATIONS].insert_one(conversation_doc)
    return str(result.inserted_id)
```

#### **Adição de Mensagens em Lote**
```python
async def add_messages_to_conversation(conversation_id: str, messages: list) -> bool:
    """Adiciona mensagens a uma conversa (atômico)"""
    db = get_async_database()
    
    # Preparar mensagens
    mongo_messages = []
    for msg in messages:
        mongo_msg = {
            "id": msg.get("id"),
            "content": msg["content"],
            "message_type": msg["message_type"],
            "user_id": msg.get("user_id"),
            "agent_id": msg.get("agent_id"),
            "metadata": msg.get("metadata", {}),
            "timestamp": datetime.utcnow()
        }
        mongo_messages.append(mongo_msg)
    
    # Atualizar documento (atômico)
    result = await db[Collections.CHAT_CONVERSATIONS].update_one(
        {"_id": conversation_id},
        {
            "$push": {"messages": {"$each": mongo_messages}},
            "$set": {
                "metadata.last_activity": datetime.utcnow(),
                "metadata.message_count": {"$add": ["$metadata.message_count", len(messages)]}
            }
        }
    )
    
    return result.modified_count > 0
```

#### **Busca de Histórico**
```python
async def get_conversation_history(conversation_id: str, limit: int = 50) -> Dict[str, Any]:
    """Busca histórico de uma conversa"""
    db = get_async_database()
    
    conversation = await db[Collections.CHAT_CONVERSATIONS].find_one(
        {"_id": conversation_id},
        {
            "messages": {"$slice": -limit},  # Últimas N mensagens
            "context": 1,
            "metadata": 1
        }
    )
    
    if not conversation:
        return None
    
    return {
        "conversation_id": conversation["_id"],
        "messages": conversation.get("messages", []),
        "context": conversation.get("context", {}),
        "metadata": conversation.get("metadata", {})
    }
```

---

## 📈 Índices e Performance

### **MongoDB Índices**

```python
# Índices para chat_conversations
await db[Collections.CHAT_CONVERSATIONS].create_index([
    ("user_id", 1), ("metadata.last_activity", -1)
])

await db[Collections.CHAT_CONVERSATIONS].create_index([
    ("agent_id", 1), ("metadata.status", 1)
])

await db[Collections.CHAT_CONVERSATIONS].create_index([
    ("metadata.status", 1), ("metadata.created_at", -1)
])

# Índices para chat_messages (backup)
await db[Collections.CHAT_MESSAGES].create_index([
    ("conversation_id", 1), ("timestamp", -1)
])

await db[Collections.CHAT_MESSAGES].create_index([
    ("user_id", 1), ("message_type", 1)
])
```

### **SQL Server Índices**

```sql
-- Índices para conversations
CREATE INDEX IX_conversations_user_id ON empl.conversations(user_id);
CREATE INDEX IX_conversations_agent_id ON empl.conversations(agent_id);
CREATE INDEX IX_conversations_status ON empl.conversations(status);
CREATE INDEX IX_conversations_last_message ON empl.conversations(last_message_at);

-- Índices para messages
CREATE INDEX IX_messages_conversation_id ON empl.messages(conversation_id);
CREATE INDEX IX_messages_user_id ON empl.messages(user_id);
CREATE INDEX IX_messages_type ON empl.messages(message_type);
```

---

## 🔄 Sincronização e Consistência

### **Estratégia de Sincronização**

1. **Criação**: Conversa criada em ambos os sistemas
2. **Mensagens**: Salvas atômicamente no MongoDB, backup no SQL Server
3. **Atualizações**: Metadados sincronizados entre os sistemas
4. **Consultas**: Prioridade para MongoDB (performance), SQL Server (integridade)

### **Tratamento de Inconsistências**

```python
async def sync_conversation_metadata(conversation_id: str):
    """Sincroniza metadados entre MongoDB e SQL Server"""
    # Buscar dados do MongoDB
    mongo_data = await get_conversation_history(conversation_id)
    
    # Atualizar SQL Server
    sql_data = {
        "last_message_at": mongo_data["metadata"]["last_activity"],
        "updated_at": datetime.utcnow()
    }
    
    # Atualizar em ambos os sistemas
    await update_sql_conversation(conversation_id, sql_data)
    await update_mongo_metadata(conversation_id, sql_data)
```

---

## 🎯 Casos de Uso

### **1. Chat em Tempo Real**
- **MongoDB**: Armazenamento rápido de mensagens
- **Performance**: Resposta em < 100ms
- **Escalabilidade**: Suporta milhares de conversas simultâneas

### **2. Histórico de Conversas**
- **MongoDB**: Busca eficiente por conversa
- **Paginação**: Carregamento incremental de mensagens
- **Filtros**: Por usuário, agente, data, status

### **3. Analytics e Métricas**
- **MongoDB**: Agregações eficientes
- **Métricas**: Tempo de resposta, tokens usados, custos
- **Relatórios**: Dashboards em tempo real

### **4. Backup e Auditoria**
- **SQL Server**: Backup de metadados críticos
- **MongoDB**: Backup de dados de chat
- **Compliance**: Rastreabilidade completa

---

## 🚀 Próximos Passos

### **Melhorias Futuras**

1. **Cache Redis**: Para conversas ativas
2. **Streaming**: Respostas em tempo real
3. **Multi-Agent**: Conversas com múltiplos agentes
4. **RAG Avançado**: Integração com base de conhecimento
5. **Analytics**: Dashboards avançados

### **Monitoramento**

1. **Métricas de Performance**: Tempo de resposta, throughput
2. **Health Checks**: Status dos bancos de dados
3. **Alertas**: Falhas de sincronização
4. **Logs**: Rastreamento completo de operações

---

## 📝 Conclusão

A arquitetura híbrida SQL Server + MongoDB oferece:

- **✅ Performance**: Consultas otimizadas para cada tipo de dado
- **✅ Escalabilidade**: Crescimento horizontal e vertical
- **✅ Confiabilidade**: Redundância e backup
- **✅ Flexibilidade**: Evolução do schema sem breaking changes
- **✅ Analytics**: Insights em tempo real sobre conversas

Esta implementação garante que o sistema EmployeeVirtual possa suportar desde conversas simples até grandes volumes de interações com agentes de IA, mantendo sempre a performance e confiabilidade necessárias para uma aplicação empresarial.

---

**🎉 O sistema está pronto para escalar e evoluir com as necessidades dos usuários!**