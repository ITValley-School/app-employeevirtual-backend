# System Agents - Catálogo IT Valley

## Visão Geral

O **System Agents** é uma funcionalidade completa de catálogo de agentes pré-configurados para diferentes necessidades empresariais. Os usuários podem descobrir, executar e gerenciar agentes especializados através de uma API robusta e bem estruturada.

## Funcionalidades Principais

### 🎯 **Catálogo de Agentes**
- **10 agentes pré-configurados** cobrindo RH, E-commerce, Marketing, Analytics e Suporte
- **Categorização** por área de negócio
- **Filtragem** por plano de usuário e região
- **Versionamento** completo com schemas de input/output

### 🚀 **Execução de Agentes**
- **Integração com Orion** para processamento de workflows
- **Execução assíncrona** com suporte a pausas e continuação
- **Auditoria completa** de todas as execuções
- **Webhooks** para notificações de status

### 🔐 **Controle de Acesso**
- **Multi-tenant** com isolamento por tenant
- **Visibilidade por plano** (FREE, BASIC, PREMIUM, ENTERPRISE)
- **Filtragem por região** geográfica
- **APIs administrativas** protegidas

### 📊 **Gestão e Monitoramento**
- **APIs de administração** para gestão completa
- **APIs de tenant** para controle específico
- **Auditoria de eventos** com rastreamento detalhado
- **Estatísticas de uso** e performance

## Estrutura do Banco de Dados

### Tabelas Criadas
1. **`agent_categories`** - Categorias dos agentes (RH, E-commerce, etc.)
2. **`system_agents`** - Catálogo principal de agentes
3. **`system_agent_versions`** - Versões dos agentes com schemas
4. **`system_agent_visibility`** - Regras de visibilidade multi-tenant
5. **`agent_execution_audit_events`** - Auditoria completa das execuções

## APIs Disponíveis

### 📱 **APIs Públicas** (`/api/system-agents`)
```
GET    /api/system-agents              # Lista catálogo de agentes
GET    /api/system-agents/{id}         # Detalhes de um agente
GET    /api/system-agents/{id}/schema  # Schema de input/output
```

### ⚡ **APIs de Execução** (`/api/executions`)
```
POST   /api/executions                 # Inicia execução
GET    /api/executions/{id}            # Status da execução
GET    /api/executions/{id}/steps      # Steps e outputs
POST   /api/executions/{id}/continue   # Continua execução pausada
POST   /api/executions/{id}/cancel     # Cancela execução
GET    /api/executions/{id}/audit      # Timeline de auditoria
```

### 🔧 **APIs Administrativas** (`/api/admin/system-agents`)
```
GET    /api/admin/system-agents              # Lista todos os agentes
POST   /api/admin/system-agents              # Cria novo agente
PUT    /api/admin/system-agents/{id}         # Atualiza agente
DELETE /api/admin/system-agents/{id}         # Remove agente

POST   /api/admin/system-agents/{id}/versions     # Cria versão
PUT    /api/admin/system-agents/{id}/versions/{v} # Atualiza versão

GET    /api/admin/system-agents/{id}/visibility   # Lista regras
POST   /api/admin/system-agents/{id}/visibility   # Cria regra
PUT    /api/admin/system-agents/{id}/visibility/{r} # Atualiza regra
```

### 🏢 **APIs de Tenant** (`/api/tenant`)
```
GET    /api/tenant/system-agents              # Catálogo do tenant
GET    /api/tenant/system-agents/stats        # Estatísticas de uso
POST   /api/tenant/system-agents/{id}/enable  # Habilita agente
POST   /api/tenant/system-agents/{id}/disable # Desabilita agente
GET    /api/tenant/executions/summary         # Resumo de execuções
```

### 🔗 **Webhooks** (`/api/webhooks`)
```
POST   /api/webhooks/orion/{execution_id}    # Webhook do Orion
```

## Agentes Pré-configurados

### 👥 **Recursos Humanos**
1. **Recrutador de Talentos IA** - Analisa perfis e encontra candidatos ideais

### 🛒 **E-commerce**
2. **Análise de Concorrência E-commerce** - Monitora preços e estratégias da concorrência

### 📢 **Marketing Digital**
3. **Gerador de Conteúdo para Redes Sociais** - Cria posts engajantes para suas redes sociais

### 📊 **Análise de Dados**
4. **Dashboard de Métricas de Vendas** - Gera relatórios completos de performance de vendas

### 🎧 **Atendimento ao Cliente**
5. **Chatbot Inteligente de Suporte** - Responde dúvidas dos clientes automaticamente

*+ 5 agentes adicionais*

## Como Usar

### 1. **Aplicar Migrações**
```bash
# Execute os scripts SQL na ordem:
scripts/001_agent_categories.sql
scripts/002_system_agents.sql
scripts/003_system_agent_versions.sql
scripts/004_system_agent_visibility.sql
scripts/005_agent_execution_audit_events.sql
```

### 2. **Popular Dados Iniciais**
```bash
cd scripts
python populate_system_agents.py
```

### 3. **Iniciar Servidor**
```bash
python main.py
```

### 4. **Testar APIs**
- Acesse: `http://localhost:8000/docs`
- Use os endpoints do **System Agents**

## Exemplo de Uso da API

### Listar Agentes Disponíveis
```python
import requests

response = requests.get(
    "http://localhost:8000/api/system-agents",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    params={"plan": "PREMIUM", "region": "us-east-1"}
)

catalog = response.json()
print(f"Agentes disponíveis: {len(catalog['agents'])}")
```

### Executar um Agente
```python
# Iniciar execução
response = requests.post(
    "http://localhost:8000/api/executions",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "system_agent_id": "agent-uuid-here",
        "params": {
            "query": "Encontrar desenvolvedores Python senior"
        },
        "auto_continue": True
    }
)

execution = response.json()
execution_id = execution["execution_id"]

# Acompanhar status
status_response = requests.get(
    f"http://localhost:8000/api/executions/{execution_id}",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

## Arquitetura Técnica

### 🗂️ **Camadas da Aplicação**
```
├── 📁 models/system_agent_models.py      # DTOs e modelos ORM
├── 📁 data/system_agent_repository.py    # Camada de dados
├── 📁 services/system_agent_service.py   # Lógica de negócio
├── 📁 api/
│   ├── 📄 system_agent_api.py           # APIs públicas
│   ├── 📄 system_agent_admin_api.py     # APIs administrativas
│   └── 📄 system_agent_tenant_api.py    # APIs de tenant
└── 📁 scripts/
    ├── 📄 001-005_*.sql                 # Migrações SQL
    └── 📄 populate_system_agents.py     # Dados iniciais
```

### 🔄 **Fluxo de Execução**
1. **Descoberta** - Usuário consulta catálogo filtrado
2. **Validação** - Sistema verifica acesso e schema
3. **Execução** - Orion processa workflows configurados
4. **Monitoramento** - Auditoria registra todos os eventos
5. **Notificação** - Webhooks informam mudanças de status

### 🛡️ **Segurança e Isolamento**
- **Autenticação JWT** em todos os endpoints
- **Filtragem multi-tenant** automática
- **Controle de visibilidade** por plano e região
- **Auditoria completa** para compliance

## Integrações

### 🚀 **Orion Executor**
- **Workflows configuráveis** por versão do agente
- **Execução assíncrona** com callbacks
- **Gerenciamento de estado** distribuído
- **Retry automático** em falhas temporárias

### 🔗 **Sistema Existente**
- **Reutiliza autenticação** atual
- **Compatível com banco** SQL Server existente
- **Integra com APIs** atuais do EmployeeVirtual

## Próximos Passos

### 🎯 **Melhorias Planejadas**
1. **Interface Web** para gestão visual do catálogo
2. **Marketplace** para agentes customizados
3. **Analytics avançadas** de uso e performance
4. **Integração com IA** para recomendações

### 📈 **Escalabilidade**
- **Cache Redis** para catálogo frequente
- **Rate limiting** por plano de usuário
- **Sharding** de execuções por região
- **CDN** para assets dos agentes

---

## 📝 **Documentação Técnica**

Para detalhes técnicos completos, consulte:
- **API_DOCUMENTATION.md** - Documentação geral da API
- **database_documentation.md** - Estrutura do banco
- **Swagger/OpenAPI** - `/docs` endpoint

## 🤝 **Contribuição**

1. Siga os padrões estabelecidos nas APIs existentes
2. Mantenha compatibilidade com multi-tenant
3. Adicione testes para novos endpoints
4. Documente mudanças no schema

---

*Sistema desenvolvido para EmployeeVirtual Backend - IT Valley*
