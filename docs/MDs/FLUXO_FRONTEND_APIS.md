# 🔄 Fluxo Completo Frontend - APIs EmployeeVirtual

## 📋 Visão Geral

Este documento explica o fluxo completo para integrar o frontend com as APIs do sistema EmployeeVirtual, incluindo autenticação, gerenciamento de agentes e chat.

## 🚪 1. Autenticação e Sessão

### 1.1 Login
- **Endpoint**: `POST /api/auth/login`
- **Descrição**: Autenticação inicial para obter tokens de acesso
- **Payload**: Email e senha do usuário
- **Resposta**: Access token e refresh token
- **Armazenamento**: Salvar tokens no localStorage ou state da aplicação

### 1.2 Refresh Token
- **Endpoint**: `POST /api/auth/refresh`
- **Descrição**: Renovar token de acesso quando expirar
- **Payload**: Refresh token atual
- **Resposta**: Novo access token

### 1.3 Headers de Autenticação
- **Obrigatório**: `Authorization: Bearer <access_token>`
- **Obrigatório**: `Content-Type: application/json` (para POST/PUT)

## 🤖 2. Gerenciamento de Agentes

### 2.1 Listar Agentes Disponíveis
- **Endpoint**: `GET /api/agents/`
- **Descrição**: Busca agentes do usuário + agentes do sistema
- **Parâmetros**: `include_system=true` (padrão)
- **Uso**: Seleção de agente para conversa

### 2.2 Agentes do Sistema
- **Endpoint**: `GET /api/agents/system`
- **Descrição**: Apenas agentes pré-configurados do sistema
- **Uso**: Mostrar opções padrão para usuários novos

### 2.3 Criar Agente Personalizado
- **Endpoint**: `POST /api/agents/`
- **Descrição**: Criar agente customizado do usuário
- **Campos obrigatórios**: Nome, system prompt, LLM provider, modelo
- **Uso**: Personalização de assistentes

### 2.4 Validar Configuração
- **Endpoint**: `POST /api/agents/validate`
- **Descrição**: Validar configuração sem criar no banco
- **Uso**: Pré-validação antes de criar agente

### 2.5 Gerenciar Agente Existente
- **Buscar**: `GET /api/agents/{agent_id}`
- **Atualizar**: `PUT /api/agents/{agent_id}`
- **Deletar**: `DELETE /api/agents/{agent_id}`

## 💬 3. Sistema de Chat

### 3.1 Enviar Mensagem
- **Endpoint**: `POST /api/chat/`
- **Descrição**: Enviar mensagem para agente específico
- **Campos obrigatórios**: Message, agent_id
- **Campo opcional**: Context (histórico, metadados)
- **Uso**: Conversa principal com o agente

### 3.2 Chat Direto com Agente (Recomendado)
- **Endpoint**: `POST /api/chat/agent`
- **Descrição**: Chat direto com agente (suporta UUIDs)
- **Campos obrigatórios**: Message, agent_id
- **Campo opcional**: Context
- **Uso**: Conversa direta com agentes personalizados e do sistema
- **Suporte**: UUIDs para agentes personalizados

### 3.3 Execução Direta do Agente
- **Endpoint**: `POST /api/agents/{agent_id}/execute`
- **Descrição**: Execução direta sem salvar no chat
- **Uso**: Testes, execuções únicas

### 3.4 Histórico de Execuções
- **Endpoint**: `GET /api/agents/{agent_id}/executions`
- **Descrição**: Listar execuções anteriores do agente
- **Parâmetros**: Limit (padrão: 50, máximo: 100)
- **Uso**: Histórico de conversas

## 📚 4. Base de Conhecimento (RAG)

### 4.1 Adicionar Arquivo
- **Endpoint**: `POST /api/agents/{agent_id}/knowledge`
- **Descrição**: Associar arquivo ao agente para contexto
- **Campos obrigatórios**: Nome, tipo, tamanho, URL
- **Campo opcional**: ID do arquivo no Orion
- **Uso**: Enriquecer conhecimento do agente

### 4.2 Listar Arquivos
- **Endpoint**: `GET /api/agents/{agent_id}/knowledge`
- **Descrição**: Listar arquivos associados ao agente
- **Uso**: Gerenciar base de conhecimento

## 🔄 5. Fluxo de Uso Recomendado

### 5.1 Inicialização da Aplicação
1. Verificar se existe token válido
2. Se não existir, redirecionar para login
3. Se existir, buscar agentes disponíveis
4. Mostrar interface de seleção de agente

### 5.2 Seleção de Agente
1. Listar agentes do usuário (se existirem)
2. Listar agentes do sistema
3. Permitir seleção ou criação de novo
4. Armazenar ID do agente selecionado

### 5.3 Início de Conversa
1. Selecionar agente ativo
2. Inicializar histórico de conversa
3. Mostrar interface de chat
4. Permitir envio de primeira mensagem

### 5.4 Conversa Ativa
1. Enviar mensagem via `/api/chat/agent` (recomendado para agentes)
2. Ou usar `/api/chat/` para sessões tradicionais
3. Receber resposta do agente
4. Atualizar histórico local
5. Manter contexto da conversa

### 5.5 Gerenciamento de Sessão
1. Monitorar validade do token
2. Renovar automaticamente quando necessário
3. Manter histórico de conversa em memória
4. Permitir troca de agente durante sessão

## ⚠️ 6. Pontos de Atenção

### 6.1 Headers Obrigatórios
- Sempre incluir `Authorization: Bearer <token>`
- Para POST/PUT: `Content-Type: application/json`

### 6.2 Tratamento de Erros
- 401: Token inválido/expirado → Redirecionar para login
- 422: Dados inválidos → Verificar formato do payload
- 500: Erro interno → Tentar novamente ou mostrar erro

### 6.3 Performance
- Cachear lista de agentes
- Limitar histórico de conversa em memória
- Implementar retry automático para falhas

### 6.4 Segurança
- Nunca armazenar tokens em localStorage (em produção)
- Implementar logout automático por inatividade
- Validar dados antes de enviar para API

## 🎯 7. Casos de Uso Típicos

### 7.1 Usuário Novo
1. Login → Listar agentes do sistema → Selecionar padrão → Iniciar conversa

### 7.2 Usuário Existente
1. Login → Listar agentes pessoais + sistema → Selecionar ou criar → Conversar

### 7.3 Múltiplas Conversas
1. Trocar entre agentes ativos
2. Manter contexto separado por agente
3. Histórico independente por conversa

### 7.4 Personalização
1. Criar agente customizado
2. Configurar personalidade e conhecimento
3. Testar antes de usar

## 📱 8. Integração com Frontend

### 8.1 Estados da Aplicação
- **Não autenticado**: Tela de login
- **Autenticado sem agente**: Seleção de agente
- **Com agente selecionado**: Interface de chat
- **Em conversa**: Chat ativo + histórico

### 8.2 Componentes Principais
- **AuthManager**: Gerenciamento de tokens e sessão
- **AgentSelector**: Lista e seleção de agentes
- **ChatInterface**: Interface de conversa
- **AgentManager**: CRUD de agentes personalizados

### 8.3 Fluxo de Dados
1. Usuário interage com interface
2. Componente chama serviço
3. Serviço faz requisição para API
4. Resposta atualiza estado local
5. Interface re-renderiza com novos dados

## 🔧 9. Configurações Recomendadas

### 9.1 Timeouts
- **Request**: 30 segundos
- **Token refresh**: 5 minutos antes da expiração
- **Retry**: Máximo 3 tentativas

### 9.2 Cache
- **Agentes**: 5 minutos
- **Configurações**: 1 hora
- **Histórico**: Em memória (últimas 100 mensagens)

### 9.3 Monitoramento
- Log de erros de API
- Métricas de performance
- Status de conectividade

## 📚 10. Recursos Adicionais

### 10.1 Documentação das APIs
- Swagger UI disponível em `/docs`
- Esquemas de request/response
- Exemplos de uso

### 10.2 Testes
- Coleção Postman disponível
- Scripts de teste automatizado
- Ambiente de desenvolvimento configurado

### 10.3 Suporte
- Logs detalhados no backend
- Tratamento de erros padronizado
- Mensagens de erro em português
