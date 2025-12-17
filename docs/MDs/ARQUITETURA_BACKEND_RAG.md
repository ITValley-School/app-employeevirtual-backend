# Arquitetura do Backend EmployeeVirtual

Este documento descreve em detalhes a arquitetura atual do backend, explicando o propósito de cada pasta e como os componentes se relacionam segundo a Clean Architecture adotada. Ao final, há um guia para replicar a mesma estrutura em um backend dedicado a um único agente de IA RAG baseado em Pinecone.

---

## Visão Geral

- **Stack principal:** FastAPI + Pydantic + SQLAlchemy + PyMongo + PydanticAI.
- **Bancos:** Azure SQL (relacional) + MongoDB (eventos/chat/RAG) + Pinecone (vetores).
- **Padrão:** IT Valley Clean Architecture (camadas claras, dependências direcionadas).

Fluxo típico de requisição:

1. `api/` recebe a chamada HTTP.
2. `schemas/` valida os dados.
3. `services/` orquestra regras de negócio.
4. `factories/` montam entidades do domínio.
5. `domain/` aplica regras centrais.
6. `data/` grava ou lê dados (SQL/Mongo/Pinecone).
7. `mappers/` preparam a resposta.

---

## Descrição das Pastas

### Camada de Entrada
- `main.py`: cria a instância FastAPI, inclui middlewares e registra rotas.
- `api/`: controladores REST (users, agents, chat, flows, dashboard, metadata, auth).
- `schemas/`: DTOs de entrada/saída por domínio (`agents/`, `chat/`, etc.).
- `middlewares/`: interceptadores (auth, CORS, logging).

### Camada de Aplicação
- `services/`: orquestram regras (ex.: `chat_service` decide quando usar RAG).
- `factories/`: constroem entidades de domínio e payloads prontos para persistência.
- `dependencies/`: providers usados pelo FastAPI para injetar serviços/repos.

### Camada de Domínio
- `domain/`: entidades e regras puras (`agents`, `chat`, `flows`, `users`).
- `dominio/`: pasta legada com modelos específicos (ex.: metadata) mantendo compatibilidade.

### Camada de Infraestrutura
- `data/`:
  - `entities/`: modelos SQLAlchemy.
  - `*_repository.py`: leitura/escrita em Azure SQL ou outros storages.
  - `chat_mongodb_repository.py`, `agent_document_repository.py`: uso do MongoDB.
  - `mongodb.py`: clientes síncrono e assíncrono (com TLS/Certifi).
  - `migrations/`: utilitários de migração SQL.
- `integrations/`:
  - `ai/`: integrações com OpenAI, Pinecone, PydanticAI (ex.: `rag_agent.py`, `ai_gateways`).
  - Outras integrações ficam nesta pasta (e.g., Orion).
- `auth/`: geração/validação de JWT, dependências de segurança.
- `config/`:
  - `settings.py`: Pydantic Settings (env vars).
  - `database.py`: engine SQL + session maker.

### Suporte
- `mappers/`: convertem entidades em respostas (AgentResponse, ChatResponse).
- `schemas/metadata`, `metadata_service`: metadados auxiliares para frontend.
- `docs/`: documentação extensa (APIs, PydanticAI, RAG, auth).
- `scripts/`: utilitários (ex.: `test_rag.py`).
- `requirements.txt`: dependências congeladas.
- `env/`: ambiente virtual local.

---

## Fluxos Específicos Importantes

### Chat + RAG
1. `chat_service.create_session` assegura que a conversa continue no mesmo session_id.
2. `chat_service.send_message` verifica se o agente tem documentos no MongoDB (`AgentDocumentRepository.has_documents`).
3. Se houver RAG disponível, delega para `AIService.generate_rag_response_sync`.
4. `AIService` usa `RagAgentRunner` (PydanticAI) que:
   - Gera embedding via OpenAI.
   - Consulta Pinecone com namespace do agente.
   - Formata os trechos (`chunk`, `content`, `text`).
   - Retorna texto consolidado para o modelo responder.

### Upload de Documentos
1. `agents_api.upload_agent_document` recebe PDF + metadados.
2. Serviço envia para microserviço externo (base URL Pinecone) via multipart/form-data.
3. Após sucesso, registra referência no MongoDB (coleção `agent_documents`).
4. Cada agente usa seu próprio namespace em Pinecone (`agent_id`).

---

## Criando um Backend Similar com um Único Agente RAG

Para replicar a arquitetura focando em apenas um agente especializado, use o seguinte roteiro:

### 1. Estrutura Base
```
novo_backend/
├── api/
├── schemas/
├── services/
├── domain/
├── data/
├── integrations/ai/
├── config/
├── auth/ (opcional, caso precise proteger o endpoint)
├── middlewares/
├── docs/
└── main.py
```

### 2. Componentes Necessários
- **Config**: mantenha `settings.py` com env vars para OpenAI/Pinecone/Mongo/SQL (mesmo que parte não seja usada agora).
- **Data Layer**:
  - Repositório simples para histórico de conversas (pode usar apenas MongoDB).
  - Repositório para documentos do agente (similar ao `agent_document_repository` mas fixo para um `AGENT_ID`).
- **Services**:
  - `chat_service` reduzido: endpoints `POST /chat` e `GET /chat/history`.
  - `ai_service`: pode manter a estrutura atual, mas com `supports_rag=True` e sem fallback multiagente.
- **Integrations/AI**:
  - Reutilize `rag_agent.py`, mas fixe o namespace (ex.: `settings.primary_agent_namespace`).
  - Ajuste prompt do `_build_agent` para especialização desejada.
- **API**:
  - Um único controller (`api/agent_api.py`) com rotas:
    - `POST /documents` (upload de PDFs, reutilizando integração com microserviço Pinecone).
    - `POST /chat` (mensagem do usuário).
    - `GET /chat/history` (opcional).
- **Docs**:
  - Crie um README simplificado explicando como subir o serviço e como configurar Pinecone.

### 3. Passo a Passo Resumido
1. Copie os diretórios `integrations/ai`, `services/ai_service.py`, `services/chat_service.py` (adapte para agente único).
2. Simplifique `AgentDocumentRepository` para usar um namespace fixo e possivelmente apenas uma coleção.
3. Remova dependências não usadas (flows, dashboard, múltiplos agentes) para enxugar a base.
4. Ajuste `main.py` para expor somente as rotas necessárias.
5. Configure `.env` mínimo (`OPENAI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_INDEX`, `MONGODB_URI`).
6. Opcional: se não precisar de SQL, elimine `config/database.py` e mantenha só Mongo + Pinecone.

### 4. Boas Práticas
- **Namespace único**: defina algo como `main_specialist_agent` e reutilize em todo o backend.
- **Prompt especializado**: ajuste `_build_agent` para contextualizar o domínio (ex.: “você é um especialista em compliance…”).
- **Logs**: mantenha apenas logs essenciais (consulta no Pinecone, resposta final).
- **Monitoramento**: implemente endpoints de health-check e métricas para saber se Pinecone/Mongo estão respondendo.

---

## Referências Rápidas
- `docs/ANALISE_EXECUCAO_AGENTE.md`: detalha execução dos agentes.
- `docs/OTIMIZACOES_RAG.md`: lições aprendidas ao otimizar o pipeline RAG.
- `docs/MDs/COMO_USAR_AGENTES_RAG.md`: melhores práticas para criação de agentes com Pinecone.

Com este guia, você pode tanto entender o funcionamento completo do backend atual quanto replicá-lo para novas instâncias especializadas em um único agente RAG. Ajuste os módulos conforme o escopo do novo projeto, mantendo a mesma organização para facilitar manutenção e evolução.


