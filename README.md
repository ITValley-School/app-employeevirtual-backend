# EmployeeVirtual Backend

Sistema backend completo desenvolvido em **Python** com **FastAPI** para a plataforma EmployeeVirtual - Uma solução robusta para criação e gerenciamento de agentes de IA, automações inteligentes e chat conversacional.

## 🎯 Visão Geral

O EmployeeVirtual Backend é uma API REST que oferece funcionalidades avançadas para:

- **🤖 Agentes de IA Personalizados** - Criação, configuração e execução de agentes inteligentes usando PydanticAI
- **🔄 Automações (Flows)** - Sistema completo de workflows automatizados para processos complexos
- **💬 Chat Inteligente** - Sistema de conversação avançado com histórico e contexto
- **📊 Dashboard e Métricas** - Análise detalhada de uso, produtividade e performance
- **📁 Processamento de Arquivos** - Upload e processamento inteligente com IA (OCR, transcrição, análise)
- **🔗 Integração Orion** - Serviços de IA prontos para uso empresarial
- **🔐 Autenticação JWT** - Sistema seguro de autenticação e autorização
- **🗄️ Banco de Dados Híbrido** - SQL Server/Azure SQL + MongoDB para máxima flexibilidade

## 🏗️ Arquitetura do Sistema

### Estrutura de Pastas

```
employeevirtual_backend/
├── � api/                     # Endpoints da API REST
│   ├── auth_api.py            # Autenticação e gestão de usuários
│   ├── agent_api.py           # Gestão de agentes de IA
│   ├── flow_api.py            # Automações e workflows
│   ├── chat_api.py            # Sistema de chat/conversação
│   ├── dashboard_api.py       # Métricas e analytics
│   └── file_api.py            # Upload e processamento de arquivos
├── 📁 data/                    # Camada de dados
│   ├── database.py            # Configuração SQL Server/Azure SQL
│   └── mongodb.py             # Configuração MongoDB
├── 📁 middlewares/             # Middlewares da aplicação
│   ├── cors_middleware.py     # CORS para frontend
│   ├── logging_middleware.py  # Sistema de logs
│   └── auth_middleware.py     # Autenticação e rate limiting
├── 📁 models/                  # Modelos de dados (Pydantic + SQLAlchemy)
│   ├── user_models.py         # Modelos de usuários
│   ├── agent_models.py        # Modelos de agentes
│   ├── flow_models.py         # Modelos de flows
│   ├── chat_models.py         # Modelos de chat
│   ├── dashboard_models.py    # Modelos de dashboard
│   └── file_models.py         # Modelos de arquivos
├── 📁 services/                # Lógica de negócio
│   ├── user_service.py        # Serviços de usuário
│   ├── agent_service.py       # Serviços de agentes
│   ├── flow_service.py        # Serviços de flows
│   ├── chat_service.py        # Serviços de chat
│   ├── dashboard_service.py   # Serviços de dashboard
│   └── orion_service.py       # Integração com serviços Orion
├── main.py                     # Aplicação principal
├── requirements.txt            # Dependências Python
├── API_DOCUMENTATION.md       # Documentação completa da API
├── database_schema.sql        # Schema do banco de dados
└── README.md                  # Este arquivo
```

## 🚀 Tecnologias e Dependências

### Core Framework
- **FastAPI 0.104.1** - Framework web moderno e rápido
- **Uvicorn 0.24.0** - Servidor ASGI de alta performance
- **Pydantic 2.5.0** - Validação de dados e serialização
- **PydanticAI 0.0.12** - Framework para agentes de IA

### Banco de Dados
- **SQLAlchemy 2.0.23** - ORM para SQL Server/Azure SQL
- **PyODBC 5.0.1** - Driver para SQL Server
- **PyMongo 4.6.0** - Driver para MongoDB
- **Motor 3.3.2** - Driver assíncrono para MongoDB

### Autenticação e Segurança
- **PyJWT 2.8.0** - Tokens JWT
- **Passlib 1.7.4** - Hash de senhas
- **Python-jose 3.3.0** - Criptografia JWT

### Integrações e Cliente HTTP
- **HTTPx** - Cliente HTTP assíncrono moderno (integrado ao FastAPI)
- **FastAPI TestClient** - Cliente para testes de integração

## 🤖 Provedores de LLM e Modelos Suportados

O EmployeeVirtual Backend suporta uma ampla gama de provedores de LLM e modelos de IA, oferecendo flexibilidade total para escolher a melhor solução para cada caso de uso.

### 🏢 Provedores Suportados

| Provedor | Código | Descrição | Status |
|----------|--------|-----------|---------|
| **OpenAI** | `openai` | GPT-4, GPT-3.5, O1, O3 e variações | ✅ Ativo |
| **Anthropic** | `anthropic` | Claude 3.5, Claude 4, Opus, Sonnet, Haiku | ✅ Ativo |
| **Google** | `google` | Gemini 1.5, Gemini 2.0, Gemini 2.5 (GLA/Vertex) | ✅ Ativo |
| **Groq** | `groq` | Llama, Gemma, Whisper, TTS | ✅ Ativo |
| **Ollama** | `ollama` | Modelos locais auto-hospedados | ✅ Ativo |
| **Mistral** | `mistral` | Mistral Large, Small, Codestral | ✅ Ativo |
| **Cohere** | `cohere` | Command R/R+, Aya Expanse | ✅ Ativo |
| **DeepSeek** | `deepseek` | DeepSeek Chat, DeepSeek Reasoner | ✅ Ativo |
| **Azure OpenAI** | `azure` | Modelos OpenAI via Azure | ✅ Ativo |

### 🎯 Modelos Principais por Categoria

#### **💬 Conversação e Chat**
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `chatgpt-4o-latest`
- **Anthropic**: `claude-3-5-sonnet-latest`, `claude-4-sonnet-20250514`, `claude-3-5-haiku-latest`
- **Google**: `gemini-2.0-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`
- **Groq**: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`

#### **🧠 Raciocínio Avançado**
- **OpenAI**: `o1`, `o1-mini`, `o3`, `o3-mini`
- **DeepSeek**: `deepseek-reasoner`
- **Groq**: `qwen-qwq-32b`, `deepseek-r1-distill-qwen-32b`

#### **💻 Programação e Código**
- **Mistral**: `codestral-latest`
- **Groq**: `qwen-2.5-coder-32b`
- **Anthropic**: `claude-3-5-sonnet-20241022` (excelente para código)

#### **🎵 Áudio e Voz**
- **OpenAI**: `gpt-4o-audio-preview`, `gpt-4o-mini-audio-preview`
- **Groq**: `whisper-large-v3`, `whisper-large-v3-turbo`, `playai-tts`

#### **🔍 Busca e Pesquisa**
- **OpenAI**: `gpt-4o-search-preview`, `gpt-4o-mini-search-preview`

#### **👁️ Visão Computacional**
- **OpenAI**: `gpt-4-vision-preview`, `gpt-4o` (com visão)
- **Groq**: `llama-3.2-11b-vision-preview`, `llama-3.2-90b-vision-preview`

### 📋 Lista Completa de Modelos Suportados

#### **OpenAI Models**
```
gpt-3.5-turbo, gpt-3.5-turbo-0125, gpt-3.5-turbo-16k
gpt-4, gpt-4-turbo, gpt-4-32k, gpt-4o, gpt-4o-mini
gpt-4o-audio-preview, gpt-4o-search-preview
gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
o1, o1-mini, o1-preview
o3, o3-mini, o4-mini
chatgpt-4o-latest
```

#### **Anthropic Models**
```
claude-2.0, claude-2.1
claude-3-haiku-20240307, claude-3-sonnet-20240229, claude-3-opus-20240229
claude-3-5-haiku-20241022, claude-3-5-sonnet-20240620, claude-3-5-sonnet-20241022
claude-3-7-sonnet-20250219
claude-4-opus-20250514, claude-4-sonnet-20250514
claude-opus-4-0, claude-sonnet-4-0
```

#### **Google Models**
```
# Google AI Studio (GLA)
gemini-1.0-pro, gemini-1.5-flash, gemini-1.5-flash-8b, gemini-1.5-pro
gemini-2.0-flash, gemini-2.0-flash-lite-preview, gemini-2.0-pro-exp
gemini-2.5-flash, gemini-2.5-pro, gemini-2.5-flash-lite-preview

# Google Vertex AI
google-vertex:gemini-1.5-pro, google-vertex:gemini-2.0-flash
google-vertex:gemini-2.5-pro, google-vertex:gemini-2.5-flash
```

#### **Groq Models**
```
# LLM Models
llama-3.3-70b-versatile, llama-3.1-8b-instant, llama3-70b-8192
qwen-qwq-32b, qwen-2.5-coder-32b, qwen-2.5-32b
mistral-saba-24b, gemma2-9b-it
deepseek-r1-distill-qwen-32b, deepseek-r1-distill-llama-70b

# Audio Models
whisper-large-v3, whisper-large-v3-turbo, distil-whisper-large-v3-en
playai-tts, playai-tts-arabic

# Vision Models  
llama-3.2-11b-vision-preview, llama-3.2-90b-vision-preview

# Other Sizes
llama-3.2-1b-preview, llama-3.2-3b-preview
```

#### **Mistral Models**
```
mistral-large-latest, mistral-small-latest
codestral-latest, mistral-moderation-latest
```

#### **Cohere Models**
```
command, command-light, command-nightly
command-r, command-r-plus, command-r7b-12-2024
c4ai-aya-expanse-32b, c4ai-aya-expanse-8b
```

#### **DeepSeek Models**
```
deepseek-chat, deepseek-reasoner
```

#### **AWS Bedrock Models**
```
# Amazon
amazon.titan-tg1-large, amazon.titan-text-lite-v1
us.amazon.nova-pro-v1:0, us.amazon.nova-lite-v1:0

# Anthropic on Bedrock
anthropic.claude-3-5-sonnet-20241022-v2:0
anthropic.claude-3-5-haiku-20241022-v1:0
anthropic.claude-3-opus-20240229-v1:0

# Meta Llama on Bedrock
meta.llama3-1-70b-instruct-v1:0
us.meta.llama3-2-90b-instruct-v1:0
us.meta.llama3-3-70b-instruct-v1:0

# Mistral on Bedrock
mistral.mistral-large-2407-v1:0
mistral.mixtral-8x7b-instruct-v0:1
```

### ⚙️ Como Configurar Modelos nos Agentes

#### **1. Criação de Agente com Modelo Específico**
```json
{
  "name": "Assistente GPT-4",
  "description": "Agente usando GPT-4o para tarefas complexas",
  "llm_provider": "openai",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 4000,
  "system_prompt": "Você é um assistente especializado..."
}
```

#### **2. Formato do Modelo no Sistema**
Os modelos são salvos no formato `provider:model` internamente:
- `openai:gpt-4o`
- `anthropic:claude-3-5-sonnet-latest`
- `google:gemini-2.0-flash`
- `groq:llama-3.3-70b-versatile`

#### **3. Configurações Recomendadas por Caso de Uso**

| Caso de Uso | Modelo Recomendado | Temperature | Max Tokens |
|-------------|-------------------|-------------|------------|
| **Chat Geral** | `gpt-4o-mini` | 0.7 | 2000 |
| **Análise Complexa** | `claude-3-5-sonnet-latest` | 0.3 | 4000 |
| **Código/Programação** | `codestral-latest` | 0.1 | 8000 |
| **Raciocínio** | `o1-mini` | 1.0 | 32000 |
| **Respostas Rápidas** | `llama-3.1-8b-instant` | 0.8 | 1000 |
| **Criativo** | `claude-3-5-haiku-latest` | 0.9 | 2000 |

### 🔧 Configuração de Provedores

Para usar diferentes provedores, configure as variáveis de ambiente:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic  
ANTHROPIC_API_KEY=your_anthropic_key

# Google
GOOGLE_API_KEY=your_google_key

# Groq
GROQ_API_KEY=your_groq_key

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint

# Outros provedores conforme necessário
```

