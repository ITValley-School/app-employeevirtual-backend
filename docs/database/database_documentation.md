# Documentação do Banco de Dados - EmployeeVirtual

## Visão Geral
O banco de dados do sistema EmployeeVirtual utiliza SQL Azure com esquema `empl` e é projetado para suportar uma plataforma SaaS de agentes de IA personalizados.

## Estrutura do Esquema

### Módulo de Usuários
- **empl.users**: Dados principais dos usuários
- **empl.user_sessions**: Sessões ativas de usuários
- **empl.user_activities**: Log de atividades dos usuários
- **empl.user_metrics**: Métricas diárias por usuário

### Módulo de Agentes
- **empl.agents**: Agentes personalizados dos usuários
- **empl.system_agents**: Agentes pré-configurados do sistema
- **empl.agent_knowledge**: Base de conhecimento dos agentes (RAG)
- **empl.agent_executions**: Histórico de execuções dos agentes
- **empl.agent_metrics**: Métricas diárias dos agentes

### Módulo de Flows/Automações
- **empl.flows**: Definição dos fluxos de automação
- **empl.flow_steps**: Etapas dos fluxos
- **empl.flow_executions**: Execuções dos fluxos
- **empl.flow_execution_steps**: Resultados das etapas
- **empl.flow_templates**: Templates de fluxos
- **empl.flow_metrics**: Métricas diárias dos fluxos

### Módulo de Chat/Conversação
- **empl.conversations**: Conversações entre usuários e agentes
- **empl.messages**: Mensagens das conversações
- **empl.conversation_contexts**: Contexto das conversações
- **empl.message_reactions**: Reações às mensagens

### Módulo de Arquivos
- **empl.files**: Arquivos enviados pelos usuários
- **empl.file_processing**: Processamentos de arquivos
- **empl.orion_services**: Serviços do Orion
- **empl.datalake_files**: Arquivos no Data Lake

### Módulo de Métricas
- **empl.system_metrics**: Métricas globais do sistema

## Relacionamentos Principais

### Usuário → Agentes
- Um usuário pode ter múltiplos agentes
- Cada agente pertence a um usuário específico

### Agente → Conhecimento
- Um agente pode ter múltiplos arquivos de conhecimento
- Cada arquivo é processado para RAG via Pinecone

### Usuário → Flows
- Um usuário pode criar múltiplos flows
- Cada flow tem múltiplas etapas sequenciais

### Conversação → Mensagens
- Uma conversação contém múltiplas mensagens
- Mensagens podem ser do usuário, agente ou sistema

### Arquivo → Processamento
- Um arquivo pode ter múltiplos processamentos
- Processamentos são feitos via Orion

## Índices e Performance

### Índices Principais
- Todos os IDs primários são auto-incrementais
- Índices em chaves estrangeiras para joins eficientes
- Índices em campos de data para consultas temporais
- Índices em campos de status para filtros

### Estratégias de Performance
- Particionamento por data nas tabelas de métricas
- Índices compostos para consultas frequentes
- Campos JSON para dados flexíveis

## Integração com Serviços Externos

### Orion (Serviços de IA)
- Todos os arquivos PDF são enviados para o Data Lake via Orion
- Processamentos de IA (OCR, transcrição, análise) via Orion
- IDs de rastreamento para monitoramento

### Pinecone (Vetorização)
- Base de conhecimento dos agentes é vetorizada
- IDs dos vetores armazenados em `agent_knowledge.vector_ids`
- Busca semântica para RAG

## Considerações de Segurança

### Dados Sensíveis
- Senhas são hasheadas (nunca em texto plano)
- Tokens de sessão com expiração
- Soft delete para dados importantes

### Auditoria
- Timestamps em todas as tabelas
- Log de atividades dos usuários
- Rastreamento de execuções

## Scripts de Manutenção

### Limpeza Automática
```sql
-- Limpar sessões expiradas
DELETE FROM empl.user_sessions WHERE expires_at < GETUTCDATE();

-- Arquivar conversações antigas
UPDATE empl.conversations 
SET status = 'archived' 
WHERE last_message_at < DATEADD(month, -6, GETUTCDATE());
```

### Agregação de Métricas
```sql
-- Agregar métricas diárias
INSERT INTO empl.user_metrics (user_id, metric_date, agent_executions, ...)
SELECT user_id, CAST(GETUTCDATE() AS DATE), COUNT(*), ...
FROM empl.agent_executions
WHERE CAST(created_at AS DATE) = CAST(GETUTCDATE() AS DATE)
GROUP BY user_id;
```

## Backup e Recuperação

### Estratégia de Backup
- Backup completo diário
- Backup incremental a cada 4 horas
- Retenção de 30 dias para backups completos
- Retenção de 7 dias para backups incrementais

### Pontos de Recuperação
- RTO (Recovery Time Objective): 1 hora
- RPO (Recovery Point Objective): 4 horas
- Testes de recuperação mensais

