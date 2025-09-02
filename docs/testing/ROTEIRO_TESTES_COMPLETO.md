# 🧪 Roteiro de Testes - EmployeeVirtual API

## 📋 **OBJETIVO**
Este roteiro orienta os desenvolvedores a testar todos os endpoints da API EmployeeVirtual de forma sistemática e completa.

---

## 🚀 **PRÉ-REQUISITOS**

### **1. Ambiente Configurado:**
- ✅ Banco de dados instalado (`database_schema_super_clean.sql`)
- ✅ Aplicação rodando (FastAPI no `main.py`)
- ✅ Postman instalado
- ✅ Coleção do Postman importada

### **2. Configuração do Postman:**
#### **2.1 Importar Arquivos**
```
1. Abra o Postman
2. File > Import
3. Selecione os arquivos da pasta: docs/testing/postman/
   - EmployeeVirtual_Agents_API.postman_collection.json
   - EmployeeVirtual-Development.postman_environment.json
   - EmployeeVirtual-Production.postman_environment.json
4. Confirme a importação
```

#### **2.2 Configurar Ambiente**
```
1. Selecione "EmployeeVirtual - Development" no dropdown de ambientes
2. Verifique se baseUrl = http://localhost:8000
3. Execute Health Check: GET /health (deve retornar 200 OK)
```

#### **2.3 Execução Automatizada**
```bash
# Teste rápido via script
cd docs/testing/postman
.\quick-test.bat

# Teste completo via PowerShell
.\run-tests.ps1

# Teste específico
.\run-tests.ps1 -TestSuite auth -OpenReport
```

### **3. Métodos de Teste Disponíveis:**
- **🎯 Manual**: Executar requests individuais no Postman
- **🏃 Semi-Auto**: Usar Collection Runner do Postman
- **🤖 Automático**: Scripts Newman via linha de comando
- **📊 Relatórios**: HTML/JSON reports automáticos

### **2. Credenciais de Teste:**
- **Admin**: `admin@employeevirtual.com` / `Soleil123`
- **Usuário Teste**: `teste@employeevirtual.com` / `123456`

### **3. URLs Base:**
- **Local**: `http://localhost:8000`
- **Desenvolvimento**: `https://dev-employeevirtual.azurewebsites.net`
- **Produção**: `https://employeevirtual.azurewebsites.net`

---

## ⚡ **INÍCIO RÁPIDO (5 MINUTOS)**

### **Opção A: Via Postman GUI**
1. **Setup**: Importe coleção + ambiente Development
2. **Health Check**: Execute `GET /health` → deve retornar 200 OK
3. **Login**: Execute `POST /auth/login` com credenciais admin → salva token automaticamente
4. **Teste Básico**: Execute `GET /users/me` → deve retornar dados do usuário
5. **Validação**: Todos os requests devem ter status 2xx

### **Opção B: Via Scripts Automáticos**
```bash
# Windows - Teste básico (2 minutos)
cd docs/testing/postman
.\quick-test.bat

# Windows - Teste completo com relatório (5 minutos)
.\run-tests.ps1 -TestSuite smoke -OpenReport

# Linux/Mac - Via Newman
newman run EmployeeVirtual_Agents_API.postman_collection.json \
  -e EmployeeVirtual-Development.postman_environment.json \
  --folder "🔐 Autenticação" --folder "👤 Usuários"
```

### **Opção C: Collection Runner**
1. **Postman**: Clique na coleção → "Run collection"
2. **Configurar**: Selecione ambiente Development + todos os requests
3. **Executar**: Clique "Run EmployeeVirtual API"
4. **Verificar**: Todos os testes devem passar (verde)

---

## 📊 **PLANO DE TESTES POR MÓDULO**

### **🔐 MÓDULO 1: AUTENTICAÇÃO (auth_api.py)**

#### **Endpoint 1.1: POST /auth/login**
**Objetivo**: Autenticar usuários e obter token JWT

**Teste 1.1.1 - Login Admin (Sucesso)**
```json
POST /auth/login
Content-Type: application/json

{
    "email": "admin@employeevirtual.com",
    "password": "Soleil123"
}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: `access_token`, `token_type`, `user_info`

**Teste 1.1.2 - Login Usuário Teste (Sucesso)**
```json
POST /auth/login
Content-Type: application/json

{
    "email": "teste@employeevirtual.com", 
    "password": "123456"
}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: `access_token`, `token_type`, `user_info`

**Teste 1.1.3 - Login Credenciais Inválidas (Erro)**
```json
POST /auth/login
Content-Type: application/json

{
    "email": "admin@employeevirtual.com",
    "password": "senha_errada"
}
```
**Resultado Esperado**: 
- Status: `401 Unauthorized`
- Retorna: `{"detail": "Invalid credentials"}`

#### **Endpoint 1.2: POST /auth/logout**
**Objetivo**: Invalidar token de acesso

**Teste 1.2.1 - Logout com Token Válido**
```
POST /auth/logout
Authorization: Bearer {token_do_login}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: `{"message": "Logged out successfully"}`

---

### **👥 MÓDULO 2: USUÁRIOS (Dentro de auth_api.py)**

#### **Endpoint 2.1: GET /auth/me**
**Objetivo**: Obter informações do usuário logado

**Teste 2.1.1 - Perfil do Admin**
```
GET /auth/me
Authorization: Bearer {admin_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: dados do admin (name, email, role: "admin")

**Teste 2.1.2 - Perfil do Usuário**
```
GET /auth/me
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: dados do usuário (name, email, role: "user")

---

### **🤖 MÓDULO 3: AGENTES (agent_api.py)**

#### **Endpoint 3.1: GET /agents**
**Objetivo**: Listar agentes do usuário

**Teste 3.1.1 - Listar Agentes do Admin**
```
GET /agents
Authorization: Bearer {admin_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: array com agentes do admin

**Teste 3.1.2 - Listar Agentes do Usuário**
```
GET /agents
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: array com agente "Programming Assistant"

#### **Endpoint 3.2: POST /agents**
**Objetivo**: Criar novo agente

**Teste 3.2.1 - Criar Agente (Sucesso)**
```json
POST /agents
Authorization: Bearer {user_token}
Content-Type: application/json

{
    "name": "Agente de Teste",
    "description": "Agente criado para testes",
    "agent_type": "custom",
    "system_prompt": "Você é um assistente de testes.",
    "personality": "Amigável e prestativo",
    "llm_provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000
}
```
**Resultado Esperado**: 
- Status: `201 Created`
- Retorna: agente criado com ID

#### **Endpoint 3.3: GET /agents/{agent_id}**
**Objetivo**: Obter detalhes de um agente específico

**Teste 3.3.1 - Obter Agente Válido**
```
GET /agents/{id_do_agente_criado}
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: detalhes completos do agente

#### **Endpoint 3.4: PUT /agents/{agent_id}**
**Objetivo**: Atualizar agente existente

**Teste 3.4.1 - Atualizar Agente**
```json
PUT /agents/{id_do_agente}
Authorization: Bearer {user_token}
Content-Type: application/json

{
    "name": "Agente de Teste Atualizado",
    "description": "Descrição atualizada",
    "temperature": 0.5
}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: agente atualizado

#### **Endpoint 3.5: DELETE /agents/{agent_id}**
**Objetivo**: Excluir agente

**Teste 3.5.1 - Excluir Agente**
```
DELETE /agents/{id_do_agente}
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: `{"message": "Agent deleted successfully"}`

#### **Endpoint 3.6: POST /agents/{agent_id}/execute**
**Objetivo**: Executar agente com uma mensagem

**Teste 3.6.1 - Executar Agente Programming Assistant**
```json
POST /agents/1/execute
Authorization: Bearer {user_token}
Content-Type: application/json

{
    "message": "Crie um código Python simples para calcular o fatorial de um número.",
    "session_id": "test_session_001"
}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: resposta gerada pelo agente

---

### **🔄 MÓDULO 4: FLOWS (flow_api.py)**

#### **Endpoint 4.1: GET /flows**
**Objetivo**: Listar flows do usuário

**Teste 4.1.1 - Listar Flows**
```
GET /flows
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: array de flows (pode estar vazio inicialmente)

#### **Endpoint 4.2: POST /flows**
**Objetivo**: Criar novo flow

**Teste 4.2.1 - Criar Flow Simples**
```json
POST /flows
Authorization: Bearer {user_token}
Content-Type: application/json

{
    "name": "Flow de Teste",
    "description": "Flow criado para testes automatizados",
    "status": "draft",
    "tags": "teste,automacao",
    "estimated_time": 120
}
```
**Resultado Esperado**: 
- Status: `201 Created`
- Retorna: flow criado com ID

#### **Endpoint 4.3: GET /flows/templates**
**Objetivo**: Listar templates de flows disponíveis

**Teste 4.3.1 - Listar Templates**
```
GET /flows/templates
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: array com 4 templates (Document Analysis, Video Transcription, Audio Processing, Code Analysis)

---

### **💬 MÓDULO 5: CHAT (chat_api.py)**

#### **Endpoint 5.1: GET /chat/conversations**
**Objetivo**: Listar conversas do usuário

**Teste 5.1.1 - Listar Conversas**
```
GET /chat/conversations
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: array de conversas

#### **Endpoint 5.2: POST /chat/conversations**
**Objetivo**: Criar nova conversa

**Teste 5.2.1 - Criar Conversa**
```json
POST /chat/conversations
Authorization: Bearer {user_token}
Content-Type: application/json

{
    "agent_id": 1,
    "title": "Conversa de Teste"
}
```
**Resultado Esperado**: 
- Status: `201 Created`
- Retorna: conversa criada

#### **Endpoint 5.3: POST /chat/conversations/{conversation_id}/messages**
**Objetivo**: Enviar mensagem em conversa

**Teste 5.3.1 - Enviar Mensagem**
```json
POST /chat/conversations/{conversation_id}/messages
Authorization: Bearer {user_token}
Content-Type: application/json

{
    "content": "Olá! Esta é uma mensagem de teste.",
    "message_type": "user"
}
```
**Resultado Esperado**: 
- Status: `201 Created`
- Retorna: mensagem criada + resposta do agente

---

### **📁 MÓDULO 6: ARQUIVOS (file_api.py)**

#### **Endpoint 6.1: GET /files**
**Objetivo**: Listar arquivos do usuário

**Teste 6.1.1 - Listar Arquivos**
```
GET /files
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: array de arquivos

#### **Endpoint 6.2: POST /files/upload**
**Objetivo**: Upload de arquivo

**Teste 6.2.1 - Upload de Arquivo Texto**
```
POST /files/upload
Authorization: Bearer {user_token}
Content-Type: multipart/form-data

file: [selecionar arquivo .txt pequeno]
description: "Arquivo de teste"
```
**Resultado Esperado**: 
- Status: `201 Created`
- Retorna: informações do arquivo uploadado

---

### **📊 MÓDULO 7: DASHBOARD (dashboard_api.py)**

#### **Endpoint 7.1: GET /dashboard/stats**
**Objetivo**: Obter estatísticas do dashboard

**Teste 7.1.1 - Estatísticas do Usuário**
```
GET /dashboard/stats
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: estatísticas (total_agents, total_flows, etc.)

#### **Endpoint 7.2: GET /dashboard/recent-activity**
**Objetivo**: Obter atividades recentes

**Teste 7.2.1 - Atividades Recentes**
```
GET /dashboard/recent-activity
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `200 OK`
- Retorna: array de atividades recentes

---

## 🔍 **TESTES DE SEGURANÇA**

### **Teste S.1: Acesso sem Token**
**Objetivo**: Verificar proteção de endpoints

**Teste S.1.1 - Endpoint Protegido sem Auth**
```
GET /agents
```
**Resultado Esperado**: 
- Status: `401 Unauthorized`
- Retorna: `{"detail": "Not authenticated"}`

### **Teste S.2: Token Inválido**
**Objetivo**: Verificar validação de token

**Teste S.2.1 - Token Malformado**
```
GET /agents
Authorization: Bearer token_invalido
```
**Resultado Esperado**: 
- Status: `401 Unauthorized`
- Retorna: `{"detail": "Invalid token"}`

### **Teste S.3: Acesso a Recursos de Outros Usuários**
**Objetivo**: Verificar isolamento de dados

**Teste S.3.1 - Tentar Acessar Agente de Outro Usuário**
```
GET /agents/{id_agente_outro_usuario}
Authorization: Bearer {user_token}
```
**Resultado Esperado**: 
- Status: `404 Not Found` ou `403 Forbidden`

---

## 📋 **CHECKLIST DE VALIDAÇÃO**

### **✅ Funcionalidades Básicas:**
- [ ] Login com credenciais corretas
- [ ] Logout funcionando
- [ ] Proteção de rotas funcionando
- [ ] CRUD de agentes completo
- [ ] CRUD de flows básico
- [ ] Sistema de chat funcionando
- [ ] Upload de arquivos funcionando
- [ ] Dashboard com dados corretos

### **✅ Segurança:**
- [ ] Autenticação obrigatória
- [ ] Tokens JWT válidos
- [ ] Isolamento entre usuários
- [ ] Validação de permissões
- [ ] Proteção contra acesso não autorizado

### **✅ Performance:**
- [ ] Responses em menos de 2 segundos
- [ ] Paginação funcionando (quando aplicável)
- [ ] Queries otimizadas
- [ ] Sem vazamentos de memória

### **✅ Dados:**
- [ ] Validação de entrada funcionando
- [ ] Tratamento de erros adequado
- [ ] Mensagens de erro claras
- [ ] Dados retornados corretos

---

## 🐛 **RELATÓRIO DE BUGS**

### **Template para Reportar Problemas:**

**Bug ID**: [Incremental]
**Módulo**: [Auth/Agents/Flows/Chat/Files/Dashboard]
**Endpoint**: [URL do endpoint]
**Severidade**: [Alta/Média/Baixa]
**Descrição**: [Descrição detalhada do problema]
**Passos para Reproduzir**: 
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

**Resultado Esperado**: [O que deveria acontecer]
**Resultado Atual**: [O que está acontecendo]
**Evidências**: [Screenshots, logs, etc.]

---

## 📞 **SUPORTE**

### **Dúvidas sobre Testes:**
- Consultar: `docs/api/API_DOCUMENTATION.md`
- Coleção Postman: `docs/testing/postman/`
- Credenciais: Ver seção "Pré-requisitos"

### **Problemas com Banco:**
- Consultar: `docs/database/DATABASE_FINAL_USAGE_GUIDE.md`
- Reinstalar: Execute `scripts/database/database_schema_super_clean.sql`

### **Problemas com Aplicação:**
- Verificar logs do FastAPI
- Consultar: `docs/INSTALLATION.md`
- Verificar se todas as dependências estão instaladas

---

## 🔧 **TROUBLESHOOTING POSTMAN**

### **Problemas Comuns e Soluções**

#### **❌ Erro: "Could not send request"**
```
Problema: Connection refused / Network error
Solução:
1. Verificar se servidor está rodando: python main.py
2. Testar URL diretamente: curl http://localhost:8000/health
3. Verificar porta 8000: netstat -an | findstr :8000
4. Verificar firewall/antivírus
```

#### **❌ Erro: "401 Unauthorized"**
```
Problema: Token inválido ou expirado
Solução:
1. Executar login novamente: POST /auth/login
2. Verificar se token foi salvo: Environment > authToken
3. Verificar Authorization Header nos requests
4. Confirmar que token não expirou (30 min)
```

#### **❌ Erro: "422 Validation Error"**
```
Problema: Dados de entrada inválidos
Solução:
1. Verificar Content-Type: application/json
2. Verificar JSON válido (sem vírgulas extras)
3. Verificar campos obrigatórios
4. Verificar tipos de dados (string, number, boolean)
```

#### **❌ Erro: "404 Not Found"**
```
Problema: Endpoint não encontrado
Solução:
1. Verificar URL base no environment
2. Verificar se endpoint existe na API
3. Verificar se ID passado é válido
4. Verificar método HTTP (GET, POST, PUT, DELETE)
```

### **Debugging Avançado**

#### **Console do Postman**
```javascript
// Adicionar nos scripts de teste para debug
console.log("Request URL:", pm.request.url);
console.log("Request Headers:", pm.request.headers);
console.log("Response Status:", pm.response.code);
console.log("Response Body:", pm.response.text());
console.log("Environment Variables:", pm.environment.toObject());
```

#### **Scripts de Validação**

**Health Check Script:**
```bash
# Windows
curl http://localhost:8000/health
# Deve retornar: {"status": "healthy"}
```

**Token Validation Script:**
```javascript
// Script de teste para validar token
pm.test("Token is valid", function () {
    const token = pm.environment.get("authToken");
    pm.expect(token).to.not.be.empty;
    pm.expect(token).to.match(/^eyJ/); // JWT starts with eyJ
});
```

---

## 🎯 **OBJETIVOS DE QUALIDADE**

### **Metas de Sucesso:**
- ✅ **100% dos endpoints** funcionando
- ✅ **Zero falhas** de segurança
- ✅ **Tempos de resposta** < 2 segundos
- ✅ **Cobertura de testes** completa
- ✅ **Documentação** atualizada

### **Critérios de Aprovação:**
- Todos os testes do checklist passando
- Relatório de bugs documentado
- Performance dentro dos padrões
- Segurança validada
- Funcionalidades core operacionais

**🚀 BOA SORTE COM OS TESTES! 🚀**
