# 🚀 Como Usar a API de Agentes com RAG

**Guia prático para criar e usar agentes RAG no EmployeeVirtual**

---

## 📋 Visão Geral do Fluxo

```
1. Criar Agente → 2. Enviar PDFs → 3. Executar Agente (RAG automático)
```

O sistema detecta automaticamente se o agente possui documentos e ativa o RAG.

---

## 🔐 Passo 0: Autenticação

Todas as requisições precisam do token JWT no header:

```http
Authorization: Bearer {seu_token_jwt}
```

**Como obter o token:**
```bash
POST /api/auth/login
{
  "email": "usuario@exemplo.com",
  "password": "senha123"
}
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 📝 Passo 1: Criar o Agente

**Endpoint:** `POST /api/agents/`

**Request:**
```json
{
  "name": "Assistente de Documentação",
  "description": "Agente especializado em responder perguntas sobre documentação técnica",
  "type": "chatbot",
  "instructions": "Você é um assistente especializado em documentação técnica. Sempre baseie suas respostas nos documentos fornecidos e seja preciso e claro.",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 2000,
  "system_prompt": "Você é um assistente de documentação técnica. Use sempre o contexto dos documentos para responder."
}
```

**Campos Obrigatórios:**
- `name`: Nome do agente (min 2 caracteres)
- `type`: Tipo do agente (`chatbot`, `assistant`, `automation`, `analyzer`)
- `instructions`: Instruções para o agente (min 3 caracteres)

**Campos Opcionais:**
- `description`: Descrição do agente
- `model`: Modelo de IA (padrão: `gpt-3.5-turbo`)
- `temperature`: Criatividade 0.0-2.0 (padrão: 0.7)
- `max_tokens`: Máximo de tokens na resposta (padrão: 1000)
- `system_prompt`: Prompt do sistema (opcional)

**Exemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/agents/" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente de Documentação",
    "type": "chatbot",
    "instructions": "Você é um assistente especializado em documentação técnica.",
    "model": "gpt-4o-mini"
  }'
```

**Resposta:**
```json
{
  "id": "abc123def456...",
  "name": "Assistente de Documentação",
  "description": "Agente especializado em responder perguntas sobre documentação técnica",
  "type": "chatbot",
  "status": "active",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 2000,
  "created_at": "2025-11-19T10:30:00Z",
  "updated_at": "2025-11-19T10:30:00Z",
  "user_id": "user123..."
}
```

**✅ Importante:** Guarde o `id` do agente para os próximos passos!

---

## 📄 Passo 2: Enviar PDFs para o Agente

**Endpoint:** `POST /api/agents/{agent_id}/documents`

**Formato:** `multipart/form-data`

**Campos:**
- `filepdf` (obrigatório): Arquivo PDF binário
- `metadone` (opcional): JSON string com metadados adicionais

**Exemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/agents/{agent_id}/documents" \
  -H "Authorization: Bearer {token}" \
  -F "filepdf=@/caminho/para/documento.pdf" \
  -F 'metadone={"curso":"IA","modulo":"1","topico":"RAG"}'
```

**Exemplo Python:**
```python
import requests

url = f"http://localhost:8000/api/agents/{agent_id}/documents"
headers = {"Authorization": f"Bearer {token}"}

# Abrir PDF
with open("documento.pdf", "rb") as pdf_file:
    files = {"filepdf": ("documento.pdf", pdf_file, "application/pdf")}
    
    # Metadados opcionais
    metadata = {
        "curso": "IA",
        "modulo": "1",
        "topico": "RAG",
        "versao": "1.0"
    }
    data = {"metadone": json.dumps(metadata)}
    
    response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
    print(response.json())
```

**Resposta de Sucesso:**
```json
{
  "message": "Documento enviado com sucesso",
  "document": {
    "agent_id": "abc123...",
    "user_id": "user123...",
    "file_name": "documento.pdf",
    "metadata": {
      "curso": "IA",
      "modulo": "1",
      "topico": "RAG",
      "agent_id": "abc123...",
      "user_id": "user123...",
      "agent_name": "Assistente de Documentação"
    },
    "created_at": "2025-11-19T10:35:00Z"
  },
  "vector_db_response": {
    "message": "Upsert realizado com sucesso. Total de chunks inseridos: 15",
    "upserted_count": 15,
    "namespace": "abc123..."
  }
}
```

**⚠️ Observações:**
- Timeout: até 120 segundos para PDFs grandes
- O microserviço processa o PDF (extração, chunking, embeddings)
- Cada chunk é inserido no Pinecone no namespace do `agent_id`
- Você pode enviar múltiplos PDFs para o mesmo agente

**❌ Erros Possíveis:**
- `400`: PDF vazio ou metadados inválidos
- `502`: Microserviço Vector DB indisponível
- `500`: Erro interno

---

## 🤖 Passo 3: Executar o Agente (RAG Automático)

**Endpoint:** `POST /api/agents/{agent_id}/execute`

**Request:**
```json
{
  "message": "O que você sabe sobre RAG?",
  "context": {},
  "session_id": null
}
```

**Campos:**
- `message` (obrigatório): Pergunta/mensagem para o agente
- `context` (opcional): Contexto adicional (dict)
- `session_id` (opcional): ID da sessão de chat

**Exemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/agents/{agent_id}/execute" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que você sabe sobre RAG?",
    "context": {},
    "session_id": null
  }'
```

**Exemplo Python:**
```python
import requests

url = f"http://localhost:8000/api/agents/{agent_id}/execute"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "message": "O que você sabe sobre RAG?",
    "context": {},
    "session_id": None
}

response = requests.post(url, headers=headers, json=payload, timeout=60)
result = response.json()

print(f"Resposta: {result['response']}")
print(f"Tempo: {result['execution_time']}s")
print(f"Tokens: {result['tokens_used']}")
```

**Resposta:**
```json
{
  "agent_id": "abc123...",
  "message": "O que você sabe sobre RAG?",
  "response": "Baseado nos documentos que você enviou, RAG (Retrieval-Augmented Generation) é uma técnica que combina busca de informações com geração de texto. O sistema busca trechos relevantes nos documentos e os usa como contexto para gerar respostas mais precisas...",
  "execution_time": 2.345,
  "tokens_used": 450,
  "session_id": null,
  "timestamp": "2025-11-19T10:40:00Z"
}
```

**🔍 Como Funciona o RAG:**

1. **Detecção Automática:** O sistema verifica se o agente possui documentos
2. **Se tiver documentos:**
   - Gera embedding da pergunta do usuário
   - Busca no Pinecone (namespace do `agent_id`, top 8 chunks)
   - Injeta contexto nos documentos no prompt
   - Gera resposta contextualizada
3. **Se não tiver documentos:**
   - Fallback para resposta padrão (sem contexto)

**✅ Validações:**
- Resposta menciona conteúdo dos PDFs enviados
- `execution_time` > 0
- `tokens_used` > 0
- Logs mostram: `🔎 Executando fluxo RAG para agente {id}`

---

## 📚 Exemplo Completo (Fluxo End-to-End)

```python
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "seu_token_jwt"

headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Criar agente
print("1. Criando agente...")
agent_data = {
    "name": "Assistente RAG",
    "type": "chatbot",
    "instructions": "Você é um assistente especializado. Use os documentos fornecidos para responder.",
    "model": "gpt-4o-mini"
}
response = requests.post(f"{BASE_URL}/api/agents/", headers=headers, json=agent_data)
agent = response.json()
agent_id = agent["id"]
print(f"✅ Agente criado: {agent_id}")

# 2. Enviar PDF
print("\n2. Enviando PDF...")
with open("documento.pdf", "rb") as f:
    files = {"filepdf": ("documento.pdf", f, "application/pdf")}
    metadata = {"topico": "RAG", "versao": "1.0"}
    data = {"metadone": json.dumps(metadata)}
    response = requests.post(
        f"{BASE_URL}/api/agents/{agent_id}/documents",
        headers=headers,
        files=files,
        data=data,
        timeout=120
    )
    print(f"✅ PDF enviado: {response.json()['vector_db_response']['upserted_count']} chunks")

# 3. Executar agente
print("\n3. Executando agente com RAG...")
payload = {
    "message": "Explique o que é RAG baseado nos documentos.",
    "context": {},
    "session_id": None
}
response = requests.post(
    f"{BASE_URL}/api/agents/{agent_id}/execute",
    headers={**headers, "Content-Type": "application/json"},
    json=payload,
    timeout=60
)
result = response.json()
print(f"✅ Resposta recebida ({result['execution_time']:.2f}s):")
print(f"   {result['response'][:200]}...")
```

---

## 🎯 Casos de Uso

### **Caso 1: Agente de Documentação Técnica**
```json
{
  "name": "Assistente de API",
  "type": "chatbot",
  "instructions": "Você é um especialista em APIs REST. Responda baseado na documentação fornecida.",
  "model": "gpt-4o-mini"
}
```
**PDFs:** Documentação da API, guias de integração

### **Caso 2: Agente de Treinamento**
```json
{
  "name": "Tutor de IA",
  "type": "assistant",
  "instructions": "Você é um tutor de Inteligência Artificial. Ensine baseado no material didático.",
  "model": "gpt-4o-mini"
}
```
**PDFs:** Apostilas, slides, materiais de curso

### **Caso 3: Agente de Suporte**
```json
{
  "name": "Suporte Técnico",
  "type": "chatbot",
  "instructions": "Você ajuda usuários com problemas técnicos. Use a base de conhecimento fornecida.",
  "model": "gpt-4o-mini"
}
```
**PDFs:** FAQs, manuais, troubleshooting

---

## 🔧 Configurações Importantes

### **Variáveis de Ambiente Necessárias:**

```bash
# OpenAI (obrigatório)
OPENAI_API_KEY=sk-...

# Pinecone (obrigatório para RAG)
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=employeevirtual-agents
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Microserviço Vector DB (para upload)
VECTOR_DB_BASE_URL=https://app-vectordb-ia.azurewebsites.net

# MongoDB (para persistência)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=mongoemploye
```

---

## ⚠️ Limitações e Observações

1. **Tamanho do PDF:** Recomendado até 10MB (timeout de 120s)
2. **Chunking:** Microserviço faz chunking automático (~1500 chars por chunk)
3. **Namespace:** Cada agente tem seu próprio namespace no Pinecone (`agent_id`)
4. **Top-K:** RAG busca top 8 chunks mais relevantes
5. **Modelo:** Usa `text-embedding-3-small` para embeddings (dimension 1536)
6. **Isolamento:** Agentes não compartilham documentos (isolamento por namespace)

---

## 🐛 Troubleshooting

### **Problema: RAG não está funcionando**
- ✅ Verificar se PDF foi enviado com sucesso
- ✅ Verificar logs: `🔎 Executando fluxo RAG para agente {id}`
- ✅ Verificar se `PINECONE_API_KEY` está configurado

### **Problema: Resposta não menciona conteúdo do PDF**
- ✅ Verificar se PDF foi processado (ver `vector_db_response`)
- ✅ Testar com pergunta mais genérica
- ✅ Verificar se chunks foram inseridos no Pinecone

### **Problema: Erro 502 no upload**
- ✅ Verificar se microserviço está acessível: `https://app-vectordb-ia.azurewebsites.net`
- ✅ Verificar timeout (pode precisar aumentar para PDFs grandes)

---

## 📊 Resumo dos Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/agents/` | POST | Criar agente |
| `/api/agents/{id}/documents` | POST | Enviar PDF |
| `/api/agents/{id}/execute` | POST | Executar agente (RAG automático) |
| `/api/agents/{id}` | GET | Buscar agente |
| `/api/agents/` | GET | Listar agentes |
| `/api/agents/{id}` | PUT | Atualizar agente |
| `/api/agents/{id}/activate` | PATCH | Ativar agente |
| `/api/agents/{id}/deactivate` | PATCH | Desativar agente |

---

**Última atualização:** 19/11/2025

