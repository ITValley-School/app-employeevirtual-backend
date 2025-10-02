# 🔑 **APIs de Gerenciamento de Chaves LLM**

## 📋 **Visão Geral**

Este documento descreve as APIs para gerenciamento de chaves LLM (Large Language Models) no sistema EmployeeVirtual. O sistema suporta dois tipos de chaves:

1. **Chaves do Sistema**: Gerenciadas por administradores enterprise
2. **Chaves do Usuário**: Gerenciadas pelos próprios usuários

## 🏗️ **Arquitetura**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Service Layer  │    │ Repository Layer│
│  (llm_api.py)   │◄──►│(llm_key_service)│◄──►│(llm_repository) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Models        │    │  Encryption     │    │   Database      │
│(llm_models.py)  │    │(LLMKeyManager)  │    │  (SQL Server)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 **Segurança e Criptografia**

### **Criptografia de Chaves**
- Todas as chaves API são criptografadas antes de serem armazenadas
- Uso da biblioteca `cryptography` com Fernet
- Chave de criptografia configurada via variável de ambiente `ENCRYPTION_KEY`

### **Controle de Acesso**
- **Chaves do Sistema**: Apenas usuários com plano `enterprise`
- **Chaves do Usuário**: Usuários podem gerenciar apenas suas próprias chaves
- Validação de JWT em todas as operações

## 📊 **Modelos de Dados**

### **Provedores Suportados**
```python
class LLMProvider(str, Enum):
    OPENAI = "openai"           # OpenAI GPT
    ANTHROPIC = "anthropic"      # Claude
    GOOGLE = "google"           # Gemini
    GROQ = "groq"               # Groq
    OLLAMA = "ollama"           # Ollama
    MISTRAL = "mistral"         # Mistral
    COHERE = "cohere"           # Cohere
    DEEPSEEK = "deepseek"       # DeepSeek
    AZURE = "azure"             # Azure OpenAI
    OPENROUTER = "openrouter"   # OpenRouter
```

### **Estrutura das Tabelas**

#### **system_llm_keys**
```sql
CREATE TABLE [empl].[system_llm_keys] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY DEFAULT NEWID(),
    provider NVARCHAR(50) NOT NULL,
    api_key NVARCHAR(500) NOT NULL, -- criptografada
    is_active BIT NOT NULL DEFAULT 1,
    usage_limit DECIMAL(10,2) NULL,
    current_usage DECIMAL(10,2) DEFAULT 0,
    last_used DATETIME2 NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL
);
```

#### **user_llm_keys**
```sql
CREATE TABLE [empl].[user_llm_keys] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY DEFAULT NEWID(),
    user_id NVARCHAR(36) NOT NULL,
    provider NVARCHAR(50) NOT NULL,
    api_key NVARCHAR(500) NOT NULL, -- criptografada
    is_active BIT NOT NULL DEFAULT 1,
    usage_limit DECIMAL(10,2) NULL,
    current_usage DECIMAL(10,2) DEFAULT 0,
    last_used DATETIME2 NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL,
    FOREIGN KEY (user_id) REFERENCES [empl].[users](id) ON DELETE CASCADE
);
```

## 🚀 **APIs Disponíveis**

### **Base URL**
```
https://seu-dominio.com/api/llm
```

### **1. Chaves do Sistema (Admin/Enterprise)**

#### **POST /system/keys**
Cria uma nova chave LLM do sistema.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Body:**
```json
{
    "provider": "openai",
    "api_key": "sk-...",
    "usage_limit": 1000.00,
    "is_active": true
}
```

**Response (201):**
```json
{
    "id": "uuid-da-chave",
    "provider": "openai",
    "usage_limit": 1000.00,
    "is_active": true,
    "current_usage": 0.0,
    "last_used": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
}
```

#### **GET /system/keys**
Lista todas as chaves LLM do sistema.

**Response (200):**
```json
[
    {
        "id": "uuid-1",
        "provider": "openai",
        "usage_limit": 1000.00,
        "is_active": true,
        "current_usage": 150.50,
        "last_used": "2024-01-15T10:30:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": "uuid-2",
        "provider": "anthropic",
        "usage_limit": 500.00,
        "is_active": true,
        "current_usage": 75.25,
        "last_used": "2024-01-14T15:45:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-14T15:45:00Z"
    }
]
```

#### **GET /system/keys/{key_id}**
Obtém uma chave específica do sistema.

**Response (200):**
```json
{
    "id": "uuid-da-chave",
    "provider": "openai",
    "usage_limit": 1000.00,
    "is_active": true,
    "current_usage": 150.50,
    "last_used": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### **PUT /system/keys/{key_id}**
Atualiza uma chave LLM do sistema.

**Body:**
```json
{
    "api_key": "sk-nova-chave...",
    "usage_limit": 1500.00,
    "is_active": false
}
```

### **2. Chaves do Usuário**

#### **POST /user/keys**
Cria uma nova chave LLM para o usuário atual.

**Body:**
```json
{
    "provider": "openai",
    "api_key": "sk-...",
    "usage_limit": 100.00,
    "is_active": true
}
```

**Response (201):**
```json
{
    "id": "uuid-da-chave",
    "user_id": "uuid-do-usuario",
    "provider": "openai",
    "usage_limit": 100.00,
    "is_active": true,
    "current_usage": 0.0,
    "last_used": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
}
```

#### **GET /user/keys**
Lista todas as chaves LLM do usuário atual.

#### **GET /user/keys/{key_id}**
Obtém uma chave específica do usuário.

#### **PUT /user/keys/{key_id}**
Atualiza uma chave LLM do usuário.

#### **DELETE /user/keys/{key_id}**
Remove uma chave LLM do usuário.

**Response (200):**
```json
{
    "message": "Chave removida com sucesso"
}
```

### **3. Validação e Estatísticas**

#### **POST /validate**
Valida uma chave API com o provedor.

**Body:**
```json
{
    "provider": "openai",
    "api_key": "sk-..."
}
```

**Response (200):**
```json
{
    "is_valid": true,
    "provider": "openai",
    "message": "Chave API válida",
    "model_info": {
        "provider": "openai",
        "status": "active"
    }
}
```

#### **GET /usage/stats**
Obtém estatísticas de uso das chaves.

**Response (200):**
```json
{
    "user_keys": [
        {
            "provider": "openai",
            "current_usage": 45.50,
            "usage_limit": 100.00,
            "usage_percentage": 45.5,
            "last_used": "2024-01-15T10:30:00Z",
            "is_active": true
        }
    ],
    "system_keys": [
        {
            "provider": "anthropic",
            "current_usage": 75.25,
            "usage_limit": 500.00,
            "usage_percentage": 15.05,
            "last_used": "2024-01-14T15:45:00Z",
            "is_active": true
        }
    ],
    "total_usage": 120.75
}
```

### **4. Provedores e Configuração**

#### **GET /providers**
Lista todos os provedores LLM disponíveis.

**Response (200):**
```json
{
    "providers": [
        {
            "value": "openai",
            "name": "Openai",
            "description": "Integração com Openai"
        },
        {
            "value": "anthropic",
            "name": "Anthropic",
            "description": "Integração com Anthropic"
        }
    ],
    "total": 10
}
```

#### **GET /agents/{agent_id}/key**
Obtém a configuração de chave de um agente.

**Response (200):**
```json
{
    "type": "user",
    "provider": "openai",
    "key_id": "uuid-da-chave"
}
```

#### **POST /agents/{agent_id}/key/validate**
Valida se a chave configurada para um agente está funcionando.

## 🔧 **Configuração do Sistema**

### **Variáveis de Ambiente**
```bash
# Chave para criptografia das chaves API
ENCRYPTION_KEY=sua-chave-de-criptografia-aqui

# Outras configurações
DATABASE_URL=sua-string-de-conexao
JWT_SECRET_KEY=sua-chave-jwt
```

### **Instalação de Dependências**
```bash
pip install -r requirements.txt
```

### **Criação das Tabelas**
```bash
# Execute o script SQL
sqlcmd -S seu-servidor -d dbmasterclasse -i scripts/database/create_llm_tables.sql
```

## 📱 **Exemplos de Uso**

### **1. Usuário Criando sua Primeira Chave**
```javascript
// Frontend - Criar chave OpenAI
const response = await fetch('/api/llm/user/keys', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        provider: 'openai',
        api_key: 'sk-...',
        usage_limit: 100.00,
        is_active: true
    })
});

const key = await response.json();
console.log('Chave criada:', key.id);
```

### **2. Validar Chave Antes de Usar**
```javascript
// Validar chave antes de criar agente
const validation = await fetch('/api/llm/validate', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        provider: 'openai',
        api_key: 'sk-...'
    })
});

const result = await validation.json();
if (result.is_valid) {
    console.log('Chave válida, pode criar agente');
} else {
    console.error('Chave inválida:', result.message);
}
```

### **3. Admin Configurando Chave do Sistema**
```javascript
// Admin enterprise configurando chave do sistema
const systemKey = await fetch('/api/llm/system/keys', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        provider: 'anthropic',
        api_key: 'sk-ant-...',
        usage_limit: 1000.00,
        is_active: true
    })
});
```

## 🚨 **Tratamento de Erros**

### **Códigos de Status HTTP**
- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Dados inválidos
- `401` - Não autorizado
- `403` - Proibido (sem permissão enterprise)
- `404` - Não encontrado
- `500` - Erro interno do servidor

### **Exemplos de Erros**
```json
{
    "detail": "Erro ao criar chave do sistema: Chave API inválida"
}
```

```json
{
    "detail": "Chave do usuário não encontrada"
}
```

## 🔒 **Considerações de Segurança**

1. **Criptografia**: Todas as chaves são criptografadas antes do armazenamento
2. **Isolamento**: Usuários só podem acessar suas próprias chaves
3. **Validação**: Chaves são validadas antes de serem aceitas
4. **Auditoria**: Todas as operações são logadas
5. **Rate Limiting**: Implementar limitação de taxa para evitar abuso

## 📈 **Monitoramento e Métricas**

### **Métricas Importantes**
- Uso por provedor
- Chaves ativas vs. inativas
- Limites de uso atingidos
- Chaves expiradas ou inválidas
- Performance das validações

### **Alertas Recomendados**
- Chave próxima do limite de uso (80%+)
- Chave inativa por mais de 30 dias
- Falha na validação de chave
- Uso anormalmente alto

## 🚀 **Próximos Passos**

1. **Implementar validação real** com cada provedor LLM
2. **Adicionar rate limiting** para as APIs
3. **Implementar webhooks** para notificações de uso
4. **Criar dashboard** para visualização de métricas
5. **Implementar rotação automática** de chaves
6. **Adicionar suporte** para chaves de teste/sandbox

---

**📚 Documentação criada em:** Janeiro 2024  
**🔄 Última atualização:** Janeiro 2024  
**👨‍💻 Desenvolvido por:** EmployeeVirtual Team
