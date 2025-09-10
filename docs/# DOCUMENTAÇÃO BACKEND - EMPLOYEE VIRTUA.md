# DOCUMENTAÇÃO BACKEND - EMPLOYEE VIRTUAL
# =====================================

## VISÃO GERAL
O backend é uma API REST construída em Python com FastAPI que gerencia conversas entre usuários e agentes virtuais criados por eles.

## ESTRUTURA DE DADOS - CHAT/CONVERSAS

### 1. TABELAS PRINCIPAIS

**conversations (empl.conversations)**
- id: UUID (chave primária)
- user_id: UUID (usuário dono da conversa)
- agent_id: UUID (agente que participa da conversa)
- title: string (título da conversa, opcional)
- status: enum [active, archived, deleted]
- created_at: datetime
- updated_at: datetime
- last_message_at: datetime

**messages (empl.messages)**
- id: UUID (chave primária)
- conversation_id: UUID (FK para conversations)
- user_id: UUID (quem enviou a mensagem)
- agent_id: UUID (opcional - preenchido se for mensagem do agente)
- content: text (conteúdo da mensagem)
- message_type: enum [user, agent, system]
- message_metadata: text (JSON string com metadados)
- created_at: datetime
- edited_at: datetime (opcional)
- is_edited: boolean

**conversation_contexts (empl.conversation_contexts)**
- id: UUID
- conversation_id: UUID (FK)
- context_key: string (chave do contexto)
- context_value: text (valor do contexto)
- created_at: datetime
- updated_at: datetime

**message_reactions (empl.message_reactions)**
- id: UUID
- message_id: UUID (FK para messages)
- user_id: UUID
- reaction_type: string (like, dislike, helpful, etc.)
- created_at: datetime

## MODELOS DE API (REQUEST/RESPONSE)

### 2. ENVIANDO MENSAGEM (CHAT)

**POST /chat**
Request Body:
```json
{
  "agent_id": "uuid-do-agente",
  "message": "Olá, como você pode me ajudar?",
  "conversation_id": "uuid-da-conversa", // opcional - se não enviado, cria nova conversa
  "context": {
    "key": "value"
  }
}
```

Response:
```json
{
  "conversation_id": "uuid-da-conversa",
  "user_message": {
    "id": "uuid",
    "content": "Olá, como você pode me ajudar?",
    "message_type": "user",
    "conversation_id": "uuid",
    "user_id": "uuid",
    "agent_id": null,
    "created_at": "2025-09-09T10:00:00Z",
    "is_edited": false,
    "metadata": {}
  },
  "agent_response": {
    "id": "uuid",
    "content": "Olá! Eu posso te ajudar com...",
    "message_type": "agent",
    "conversation_id": "uuid",
    "user_id": "uuid",
    "agent_id": "uuid-do-agente",
    "created_at": "2025-09-09T10:00:01Z",
    "is_edited": false,
    "metadata": {}
  },
  "agent_name": "Nome do Agente",
  "execution_time": 1.5,
  "tokens_used": 150
}
```

### 3. CRIANDO CONVERSA

**POST /conversations**
Request:
```json
{
  "agent_id": "uuid-do-agente",
  "title": "Título da conversa" // opcional
}
```

Response:
```json
{
  "id": "uuid-da-conversa",
  "user_id": "uuid-do-usuario",
  "agent_id": "uuid-do-agente",
  "agent_name": "Nome do Agente",
  "title": "Título da conversa",
  "status": "active",
  "message_count": 0,
  "created_at": "2025-09-09T10:00:00Z",
  "updated_at": null,
  "last_message_at": null
}
```

### 4. LISTANDO CONVERSAS DO USUÁRIO

**GET /conversations**
Query params:
- status: active|archived|deleted (opcional)
- agent_id: uuid (opcional - filtrar por agente)
- limit: int (padrão 20)
- offset: int (padrão 0)

Response:
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "agent_id": "uuid",
    "agent_name": "Nome do Agente",
    "title": "Título",
    "status": "active",
    "message_count": 5,
    "created_at": "2025-09-09T10:00:00Z",
    "updated_at": "2025-09-09T11:00:00Z",
    "last_message_at": "2025-09-09T11:00:00Z"
  }
]
```

### 5. OBTENDO CONVERSA COM MENSAGENS

**GET /conversations/{conversation_id}**
Response:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "agent_id": "uuid",
  "agent_name": "Nome do Agente",
  "title": "Título",
  "status": "active",
  "message_count": 2,
  "created_at": "2025-09-09T10:00:00Z",
  "messages": [
    {
      "id": "uuid",
      "content": "Olá!",
      "message_type": "user",
      "created_at": "2025-09-09T10:00:00Z",
      // ... outros campos
    },
    {
      "id": "uuid",
      "content": "Olá! Como posso ajudar?",
      "message_type": "agent",
      "created_at": "2025-09-09T10:00:01Z",
      // ... outros campos
    }
  ]
}
```

### 6. ATUALIZANDO CONVERSA

**PUT /conversations/{conversation_id}**
Request:
```json
{
  "title": "Novo título",
  "status": "archived"
}
```

### 7. TIPOS DE DADOS IMPORTANTES

**MessageType:**
- "user": Mensagem enviada pelo usuário
- "agent": Mensagem enviada pelo agente
- "system": Mensagem do sistema

**ConversationStatus:**
- "active": Conversa ativa
- "archived": Conversa arquivada
- "deleted": Conversa deletada

## FLUXO TÍPICO DE USO

1. **Nova Conversa:**
   - Frontend chama POST /chat com agent_id e message (sem conversation_id)
   - Backend cria nova conversa e primeira mensagem
   - Agente processa e responde
   - Retorna conversa com mensagens do usuário e agente

2. **Continuando Conversa:**
   - Frontend chama POST /chat com agent_id, message e conversation_id
   - Backend adiciona mensagem à conversa existente
   - Agente processa considerando histórico
   - Retorna novas mensagens

3. **Listando Conversas:**
   - Frontend chama GET /conversations para listar conversas do usuário
   - Pode filtrar por status ou agente

4. **Carregando Histórico:**
   - Frontend chama GET /conversations/{id} para carregar mensagens completas

## AUTENTICAÇÃO
- Todas as rotas requerem token JWT
- user_id é extraído do token automaticamente
- Usuário só pode acessar suas próprias conversas

## CONSIDERAÇÕES TÉCNICAS
- Todas as IDs são UUIDs
- Datas em formato ISO 8601 com timezone
- Mensagens têm limite de tamanho (configurável)
- Contexto das conversas é preservado automaticamente
- Sistema suporta reações às mensagens (like/dislike)

## ESTRUTURA DE ERROS
```json
{
  "detail": "Mensagem de erro específica",
  "error_code": "CONVERSATION_NOT_FOUND",
  "timestamp": "2025-09-09T10:00:00Z"
}
```

Códigos HTTP comuns:
- 200: Sucesso
- 201: Criado
- 400: Dados inválidos
- 401: Não autenticado
- 403: Sem permissão
- 404: Não encontrado
- 500: Erro interno

## OBSERVAÇÕES PARA O FRONTEND
- Sempre incluir Authorization header com Bearer token
- conversation_id é opcional na primeira mensagem de uma conversa
- message_count é calculado automaticamente
- last_message_at é atualizado automaticamente
- Metadados das mensagens podem conter informações extras do agente
- Sistema preserva ordem