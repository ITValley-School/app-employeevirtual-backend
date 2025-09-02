# Documentação da API - EmployeeVirtual

Esta documentação fornece informações detalhadas sobre todos os endpoints da API do sistema EmployeeVirtual.

## 📚 Visão Geral

A API do EmployeeVirtual é uma API REST construída com FastAPI que oferece funcionalidades completas para:

- **Autenticação e gestão de usuários**
- **Criação e execução de agentes de IA**
- **Automações e workflows (flows)**
- **Chat e conversação com agentes**
- **Dashboard e métricas de uso**
- **Upload e processamento de arquivos**

**Base URL:** `http://localhost:8000/api`

**Documentação interativa:** `http://localhost:8000/docs`

## 🔐 Autenticação

A API utiliza autenticação JWT (JSON Web Tokens). Após o login, inclua o token no header de todas as requisições:

```
Authorization: Bearer <seu_token_jwt>
```

### Endpoints de Autenticação

#### POST /auth/register
Registra um novo usuário no sistema.

**Request Body:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "is_active": true
}
```

#### POST /auth/login
Autentica um usuário e retorna token JWT.

**Request Body:**
```json
{
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2024-01-02T10:00:00Z",
  "user": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@example.com"
  }
}
```

#### GET /auth/me
Retorna informações do usuário atual.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com",
  "created_at": "2024-01-01T10:00:00Z",
  "is_active": true
}
```

## 🤖 Agentes de IA

### GET /agents/
Lista todos os agentes do usuário.

**Query Parameters:**
- `include_system` (boolean): Incluir agentes do sistema (padrão: true)

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Assistente de Vendas",
    "description": "Agente especializado em vendas",
    "instructions": "Você é um assistente de vendas...",
    "model": "gpt-4",
    "is_system": false,
    "is_active": true,
    "usage_count": 15,
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### POST /agents/
Cria um novo agente personalizado.

**Request Body:**
```json
{
  "name": "Assistente de Marketing",
  "description": "Agente para estratégias de marketing",
  "instructions": "Você é um especialista em marketing digital...",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response (201):**
```json
{
  "id": 2,
  "user_id": 1,
  "name": "Assistente de Marketing",
  "description": "Agente para estratégias de marketing",
  "instructions": "Você é um especialista em marketing digital...",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000,
  "is_system": false,
  "is_active": true,
  "usage_count": 0,
  "created_at": "2024-01-01T11:00:00Z"
}
```

### GET /agents/{agent_id}
Busca um agente específico por ID.

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Assistente de Vendas",
  "description": "Agente especializado em vendas",
  "instructions": "Você é um assistente de vendas...",
  "model": "gpt-4",
  "is_system": false,
  "is_active": true,
  "usage_count": 15,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### POST /agents/{agent_id}/execute
Executa um agente com uma mensagem do usuário.

**Request Body:**
```json
{
  "user_message": "Como posso melhorar minhas vendas online?",
  "context": {
    "produto": "software",
    "mercado": "B2B"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "response": "Para melhorar suas vendas online de software B2B, recomendo...",
  "agent_name": "Assistente de Vendas",
  "execution_time": 2.5,
  "model_used": "gpt-4",
  "tokens_used": 150
}
```

## 🔄 Flows (Automações)

### GET /flows/
Lista todos os flows do usuário.

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Análise de Documento",
    "description": "Flow para analisar documentos PDF",
    "status": "active",
    "tags": ["análise", "documento"],
    "execution_count": 5,
    "estimated_time": 120,
    "created_at": "2024-01-01T10:00:00Z",
    "steps": [
      {
        "id": 1,
        "name": "Upload do arquivo",
        "step_type": "file_upload",
        "order": 1
      },
      {
        "id": 2,
        "name": "Análise com IA",
        "step_type": "orion_service",
        "order": 2,
        "config": {
          "service_type": "pdf_analysis"
        }
      }
    ]
  }
]
```

### POST /flows/
Cria um novo flow.

**Request Body:**
```json
{
  "name": "Transcrição de Áudio",
  "description": "Flow para transcrever arquivos de áudio",
  "tags": ["áudio", "transcrição"],
  "steps": [
    {
      "name": "Upload do áudio",
      "step_type": "file_upload",
      "order": 1,
      "description": "Upload do arquivo de áudio"
    },
    {
      "name": "Transcrição",
      "step_type": "orion_service",
      "order": 2,
      "description": "Transcrever áudio para texto",
      "config": {
        "service_type": "transcription",
        "language": "pt-BR"
      }
    }
  ]
}
```

### POST /flows/{flow_id}/execute
Executa um flow com dados de entrada.

**Request Body:**
```json
{
  "input_data": {
    "file_url": "https://example.com/audio.mp3"
  },
  "auto_continue": true
}
```

**Response (200):**
```json
{
  "id": 1,
  "flow_id": 1,
  "flow_name": "Transcrição de Áudio",
  "status": "completed",
  "input_data": {
    "file_url": "https://example.com/audio.mp3"
  },
  "output_data": {
    "transcription": "Olá, este é um teste de transcrição..."
  },
  "execution_time": 45.2,
  "started_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:00:45Z"
}
```

## 💬 Chat e Conversação

### POST /chat/send
Envia uma mensagem para um agente e recebe resposta.

**Request Body:**
```json
{
  "agent_id": 1,
  "message": "Olá, como você pode me ajudar?",
  "conversation_id": null,
  "context": {}
}
```

**Response (200):**
```json
{
  "conversation_id": 1,
  "user_message": {
    "id": 1,
    "content": "Olá, como você pode me ajudar?",
    "message_type": "user",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "agent_response": {
    "id": 2,
    "content": "Olá! Sou seu assistente de vendas...",
    "message_type": "agent",
    "created_at": "2024-01-01T12:00:02Z"
  },
  "agent_name": "Assistente de Vendas",
  "execution_time": 2.1
}
```

### GET /chat/conversations
Lista conversações do usuário.

**Query Parameters:**
- `limit` (integer): Limite de conversações (padrão: 50)

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Conversa com Assistente de Vendas",
    "agent_name": "Assistente de Vendas",
    "message_count": 8,
    "last_message_preview": "Obrigado pela ajuda!",
    "last_message_at": "2024-01-01T12:30:00Z",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### GET /chat/conversations/{conversation_id}
Busca uma conversação com todas as mensagens.

**Response (200):**
```json
{
  "id": 1,
  "title": "Conversa com Assistente de Vendas",
  "agent_name": "Assistente de Vendas",
  "message_count": 4,
  "created_at": "2024-01-01T12:00:00Z",
  "messages": [
    {
      "id": 1,
      "content": "Olá, como você pode me ajudar?",
      "message_type": "user",
      "created_at": "2024-01-01T12:00:00Z"
    },
    {
      "id": 2,
      "content": "Olá! Sou seu assistente de vendas...",
      "message_type": "agent",
      "created_at": "2024-01-01T12:00:02Z"
    }
  ]
}
```

## 📊 Dashboard e Métricas

### GET /dashboard/
Retorna dados completos do dashboard do usuário.

**Response (200):**
```json
{
  "summary": {
    "total_agents": 5,
    "total_flows": 3,
    "total_executions_today": 12,
    "total_executions_all_time": 150,
    "active_flows": 2,
    "time_saved_today": 2.5,
    "time_saved_all_time": 45.8
  },
  "top_agents": [
    {
      "agent_id": 1,
      "agent_name": "Assistente de Vendas",
      "total_executions": 50,
      "executions_today": 5,
      "average_execution_time": 2.3,
      "success_rate": 98.5
    }
  ],
  "usage_chart": {
    "labels": ["01/01", "02/01", "03/01"],
    "datasets": [
      {
        "label": "Execuções de Agentes",
        "data": [10, 15, 12],
        "borderColor": "#3B82F6"
      }
    ]
  }
}
```

### GET /dashboard/usage
Busca métricas de uso por período.

**Query Parameters:**
- `start_date` (date): Data inicial (YYYY-MM-DD)
- `end_date` (date): Data final (YYYY-MM-DD)
- `days` (integer): Número de dias (alternativa)

**Response (200):**
```json
[
  {
    "date": "2024-01-01",
    "agent_executions": 10,
    "flow_executions": 3,
    "file_uploads": 5,
    "chat_messages": 25,
    "time_saved": 2.5
  }
]
```

## 📁 Arquivos

### POST /files/upload
Faz upload de um arquivo.

**Request (multipart/form-data):**
- `file`: Arquivo a ser enviado
- `description`: Descrição do arquivo (opcional)
- `tags`: Tags separadas por vírgula (opcional)
- `process_with_orion`: Processar com IA (padrão: true)

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "original_filename": "documento.pdf",
  "stored_filename": "uuid-documento.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "description": "Contrato de vendas",
  "tags": ["contrato", "vendas"],
  "datalake_url": "https://datalake.com/files/uuid-documento.pdf",
  "processed": true,
  "processing_result": {
    "text": "Conteúdo extraído do PDF...",
    "pages": 5
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

### GET /files/
Lista arquivos do usuário.

**Query Parameters:**
- `file_type` (string): Filtrar por tipo de arquivo
- `limit` (integer): Limite de arquivos (padrão: 50)

**Response (200):**
```json
[
  {
    "id": 1,
    "original_filename": "documento.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "description": "Contrato de vendas",
    "tags": ["contrato", "vendas"],
    "processed": true,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### POST /files/{file_id}/process
Processa um arquivo com serviços de IA.

**Request Body:**
```json
{
  "service_type": "pdf_analysis"
}
```

**Response (200):**
```json
{
  "message": "Arquivo processado com sucesso",
  "result": {
    "text": "Conteúdo extraído...",
    "summary": "Resumo do documento...",
    "entities": ["João Silva", "Empresa XYZ"]
  },
  "task_id": "orion-task-123"
}
```

## 🔍 Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Token inválido ou ausente |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Erro de validação |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Erro interno |

## 🚨 Tratamento de Erros

Todas as respostas de erro seguem o formato padrão:

```json
{
  "error": true,
  "message": "Descrição do erro",
  "status_code": 400,
  "path": "/api/agents/999"
}
```

### Exemplos de Erros Comuns

**Token inválido (401):**
```json
{
  "error": true,
  "message": "Token inválido ou expirado",
  "status_code": 401,
  "path": "/api/agents/"
}
```

**Recurso não encontrado (404):**
```json
{
  "error": true,
  "message": "Agente não encontrado",
  "status_code": 404,
  "path": "/api/agents/999"
}
```

**Dados inválidos (422):**
```json
{
  "error": true,
  "message": "Validation error",
  "status_code": 422,
  "details": [
    {
      "field": "email",
      "message": "Email inválido"
    }
  ]
}
```

## 📝 Rate Limiting

A API implementa rate limiting para prevenir abuso:

- **Limite padrão:** 1000 requisições por minuto por IP
- **Headers de resposta:**
  - `X-RateLimit-Limit`: Limite total
  - `X-RateLimit-Remaining`: Requisições restantes
  - `X-RateLimit-Reset`: Timestamp do reset

## 🔧 Webhooks (Futuro)

*Funcionalidade planejada para versões futuras*

## 📚 SDKs e Bibliotecas

### JavaScript/TypeScript
```javascript
// Exemplo de uso com fetch
const response = await fetch('http://localhost:8000/api/agents/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const agents = await response.json();
```

### Python
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/agents/', headers=headers)
agents = response.json()
```

### cURL
```bash
curl -X GET "http://localhost:8000/api/agents/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## 🔄 Versionamento

A API utiliza versionamento semântico:
- **v1.0.0**: Versão inicial
- Mudanças breaking serão indicadas por incremento da versão major
- Novas funcionalidades incrementam a versão minor
- Correções incrementam a versão patch

## 📞 Suporte

Para dúvidas sobre a API:
- **Documentação interativa:** `/docs`
- **Email:** api-support@employeevirtual.com
- **GitHub Issues:** Para reportar bugs
- **Discord:** Comunidade de desenvolvedores

