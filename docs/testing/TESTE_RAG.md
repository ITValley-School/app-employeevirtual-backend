# 🧪 Guia de Testes - Sistema RAG com Pinecone

**Data:** 19/11/2025  
**Versão:** 1.0.0

## 📋 Pré-requisitos

### 1. Variáveis de Ambiente

Certifique-se de ter configurado no `.env`:

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

# MongoDB (para persistência de documentos)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=mongoemploye

# JWT (para autenticação)
JWT_SECRET_KEY=your-secret-key
```

### 2. Serviços em Execução

- ✅ Backend FastAPI rodando (`uvicorn main:app --reload`)
- ✅ Microserviço Vector DB acessível (`https://app-vectordb-ia.azurewebsites.net`)
- ✅ MongoDB conectado
- ✅ Pinecone index criado (ou será criado automaticamente)

---

## 🚀 Fluxo de Testes

### **Teste 1: Criar Agente**

**Endpoint:** `POST /api/agents/`

**Request:**
```json
{
  "name": "Agente RAG Teste",
  "description": "Agente para testar RAG",
  "type": "chatbot",
  "instructions": "Você é um assistente especializado em responder perguntas baseado em documentos.",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Headers:**
```
Authorization: Bearer {seu_token_jwt}
Content-Type: application/json
```

**Resposta Esperada:**
```json
{
  "id": "abc123...",
  "name": "Agente RAG Teste",
  "status": "active",
  ...
}
```

**✅ Validação:** Anotar o `agent_id` retornado para próximos testes.

---

### **Teste 2: Upload de PDF para o Agente**

**Endpoint:** `POST /api/agents/{agent_id}/documents`

**Request (multipart/form-data):**
- `filepdf`: arquivo PDF (ex: `documento_teste.pdf`)
- `metadone` (opcional): JSON string com metadados
  ```json
  {"curso": "IA", "modulo": "1", "topico": "RAG"}
  ```

**Exemplo cURL:**
```bash
curl -X POST "http://localhost:8000/api/agents/{agent_id}/documents" \
  -H "Authorization: Bearer {token}" \
  -F "filepdf=@/caminho/para/documento.pdf" \
  -F 'metadone={"curso":"IA","modulo":"1"}'
```

**Exemplo Python (requests):**
```python
import requests

url = "http://localhost:8000/api/agents/{agent_id}/documents"
headers = {"Authorization": f"Bearer {token}"}

files = {"filepdf": open("documento.pdf", "rb")}
data = {"metadone": '{"curso":"IA","modulo":"1"}'}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

**Resposta Esperada:**
```json
{
  "message": "Documento enviado com sucesso",
  "document": {
    "agent_id": "abc123...",
    "file_name": "documento.pdf",
    "metadata": {...},
    "created_at": "2025-11-19T..."
  },
  "vector_db_response": {
    "message": "...",
    "upserted_count": 10
  }
}
```

**✅ Validações:**
- Status `201 Created`
- `vector_db_response` contém resposta do microserviço
- Documento salvo no MongoDB

**❌ Erros Possíveis:**
- `400`: PDF vazio ou metadados inválidos
- `502`: Microserviço Vector DB indisponível
- `500`: Erro interno

---

### **Teste 3: Executar Agente com RAG**

**Endpoint:** `POST /api/agents/{agent_id}/execute`

**Request:**
```json
{
  "message": "O que você sabe sobre o conteúdo do documento que enviei?",
  "context": {},
  "session_id": null
}
```

**Resposta Esperada:**
```json
{
  "agent_id": "abc123...",
  "message": "O que você sabe sobre...",
  "response": "Baseado nos documentos que você enviou, posso informar que...",
  "execution_time": 2.345,
  "tokens_used": 450,
  "session_id": null,
  "timestamp": "2025-11-19T..."
}
```

**✅ Validações:**
- Resposta menciona conteúdo do PDF enviado
- `execution_time` > 0
- `tokens_used` > 0

**🔍 Verificar Logs:**
```
🔎 Executando fluxo RAG para agente abc123...
Buscando contexto no namespace abc123...
Consulta Pinecone namespace=abc123 retornou 8 matches
```

---

### **Teste 4: Executar Agente SEM Documentos (Fallback)**

**Cenário:** Executar agente que não possui documentos enviados.

**Request:** Mesmo do Teste 3, mas com `agent_id` diferente (sem documentos).

**Resposta Esperada:**
```json
{
  "response": "Desculpe, não tenho conhecimento específico sobre isso...",
  "rag_used": false
}
```

**✅ Validações:**
- Resposta genérica (não menciona documentos)
- Logs mostram: `Agente {id} não possui documentos para RAG`
- Fallback para resposta padrão funcionando

---

### **Teste 5: Listar Documentos do Agente**

**Endpoint:** `GET /api/agents/{agent_id}/documents` (se implementado)

Ou verificar diretamente no MongoDB:
```javascript
db.agent_documents.find({ agent_id: "abc123..." })
```

**✅ Validações:**
- Documentos listados corretamente
- Metadados preservados
- Timestamps corretos

---

## 🔍 Verificações no Pinecone

### Via Python:

```python
from pinecone import Pinecone

pc = Pinecone(api_key="sua_key")
index = pc.Index("employeevirtual-agents")

# Verificar stats do namespace
stats = index.describe_index_stats()
print(stats.namespaces)  # Deve mostrar o agent_id como namespace

# Query manual para testar
from openai import OpenAI
openai_client = OpenAI(api_key="sua_key")

query_text = "teste"
embedding = openai_client.embeddings.create(
    input=query_text,
    model="text-embedding-3-small"
).data[0].embedding

results = index.query(
    vector=embedding,
    top_k=5,
    include_metadata=True,
    namespace="abc123..."  # agent_id
)

print(f"Encontrados {len(results.matches)} matches")
for match in results.matches:
    print(f"Score: {match.score}, Content: {match.metadata.get('content', '')[:100]}")
```

---

## 🐛 Testes de Erro

### **Teste 6: Upload com PDF Inválido**

**Request:** Enviar arquivo que não é PDF (ex: `.txt`)

**Esperado:** `400 Bad Request` ou erro do microserviço

---

### **Teste 7: Upload com Metadados Inválidos**

**Request:** `metadone` com JSON malformado

**Esperado:** `400 Bad Request` - "Metadados inválidos. Envie um JSON válido."

---

### **Teste 8: Executar Agente Inexistente**

**Request:** `agent_id` que não existe

**Esperado:** `400 Bad Request` - "Agente não encontrado"

---

### **Teste 9: RAG com Pinecone Indisponível**

**Cenário:** Desabilitar `PINECONE_API_KEY` temporariamente

**Esperado:** Fallback para resposta padrão, log de warning

---

## 📊 Checklist de Validação

- [ ] Agente criado com sucesso
- [ ] PDF enviado e processado pelo microserviço
- [ ] Documento persistido no MongoDB
- [ ] Execução RAG retorna resposta contextualizada
- [ ] Fallback funciona quando não há documentos
- [ ] Logs mostram fluxo RAG correto
- [ ] Pinecone contém vectors no namespace do agente
- [ ] Erros tratados corretamente (400, 502, 500)

---

## 🎯 Testes Avançados

### **Teste 10: Múltiplos PDFs no Mesmo Agente**

1. Enviar 3 PDFs diferentes para o mesmo agente
2. Executar pergunta que requer conhecimento de múltiplos documentos
3. Validar que resposta combina informações de todos

---

### **Teste 11: Agentes Isolados**

1. Criar 2 agentes diferentes
2. Enviar PDFs específicos para cada um
3. Executar mesma pergunta em ambos
4. Validar que respostas são diferentes (isolamento por namespace)

---

## 📝 Notas Importantes

1. **Timeout:** Upload de PDFs grandes pode levar até 120s (configurado no `VectorDBClient`)
2. **Namespace:** Cada agente usa seu `agent_id` como namespace no Pinecone
3. **Chunking:** Microserviço faz chunking automático (tamanho padrão: ~1500 chars)
4. **Embeddings:** Usa `text-embedding-3-small` (dimension 1536)
5. **Top-K:** RAG busca top 8 chunks mais relevantes

---

## 🆘 Troubleshooting

### Problema: "RAG desabilitado"
**Solução:** Verificar se `PINECONE_API_KEY` e `PINECONE_INDEX_NAME` estão configurados

### Problema: "502 Bad Gateway" no upload
**Solução:** Verificar se microserviço `https://app-vectordb-ia.azurewebsites.net` está acessível

### Problema: Resposta não menciona conteúdo do PDF
**Solução:** 
- Verificar se PDF foi processado corretamente
- Verificar logs do Pinecone query
- Testar query manual no Pinecone

### Problema: "Nenhum conhecimento relevante encontrado"
**Solução:** 
- Verificar se vectors foram inseridos no namespace correto
- Testar com query mais genérica
- Verificar se embedding da query está correto

---

**Última atualização:** 19/11/2025

