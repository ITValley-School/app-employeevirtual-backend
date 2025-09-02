# Guia de Configuração do Postman - EmployeeVirtual API

## 📋 Visão Geral

Este guia fornece instruções detalhadas para configurar e usar a coleção Postman do EmployeeVirtual API, incluindo configuração de ambiente, autenticação e execução de testes.

## 🚀 Configuração Inicial

### 1. Importar a Coleção

1. Abra o Postman
2. Clique em "Import"
3. Selecione o arquivo `EmployeeVirtual_Agents_API.postman_collection.json`
4. Confirme a importação

### 2. Configurar Ambiente

Crie um novo ambiente no Postman com as seguintes variáveis:

```json
{
  "baseUrl": "http://localhost:8000",
  "authToken": "",
  "userId": "",
  "agentId": "",
  "chatId": "",
  "flowId": "",
  "serviceId": "",
  "messageId": "",
  "fileId": ""
}
```

### 3. Configuração de Desenvolvimento Local

Para desenvolvimento local, configure as variáveis:

- `baseUrl`: `http://localhost:8000`
- Outras variáveis serão preenchidas automaticamente durante os testes

### 4. Configuração de Produção

Para ambiente de produção, ajuste:

- `baseUrl`: URL do seu servidor de produção
- Configure SSL/TLS conforme necessário

## 🔐 Autenticação e Tokens

### Configuração de Token Automática

A coleção está configurada para:

1. **Login Automático**: O primeiro request de login armazena o token automaticamente
2. **Token Persistente**: O token é salvo na variável `authToken` do ambiente
3. **Autorização Automática**: Todos os requests protegidos usam o token automaticamente

### Scripts de Pré-requisito

Os requests incluem scripts que:

- Extraem IDs de resposta automaticamente
- Armazenam variáveis para uso posterior
- Validam respostas e configurações

## 📝 Credenciais de Teste

### Usuário Admin (Criado automaticamente)
```
Email: admin@employeevirtual.com
Senha: admin123
```

### Usuário Teste (Criado via API)
```
Email: teste@exemplo.com
Senha: senha123
```

## 🧪 Executando Testes

### Ordem Recomendada de Execução

1. **Autenticação**
   - POST `/auth/register` (criar usuário teste)
   - POST `/auth/login` (obter token)

2. **Gestão de Usuários**
   - GET `/users/me` (perfil do usuário)
   - PUT `/users/me` (atualizar perfil)

3. **Agentes**
   - POST `/agents` (criar agente)
   - GET `/agents` (listar agentes)
   - GET `/agents/{id}` (detalhes do agente)
   - PUT `/agents/{id}` (atualizar agente)

4. **Chats**
   - POST `/chats` (criar chat)
   - GET `/chats` (listar chats)
   - POST `/chats/{id}/messages` (enviar mensagem)

5. **Fluxos**
   - POST `/flows` (criar fluxo)
   - GET `/flows` (listar fluxos)
   - PUT `/flows/{id}` (atualizar fluxo)

6. **Arquivos**
   - POST `/files/upload` (upload de arquivo)
   - GET `/files` (listar arquivos)
   - GET `/files/{id}` (baixar arquivo)

7. **Dashboard**
   - GET `/dashboard/stats` (estatísticas)
   - GET `/dashboard/recent-activity` (atividade recente)

### Execução em Lote

Para executar todos os testes de uma vez:

1. Selecione a coleção completa
2. Clique em "Run collection"
3. Configure o ambiente apropriado
4. Execute os testes em sequência

## 🔍 Validação e Debugging

### Scripts de Teste Automáticos

Cada request inclui scripts de teste que validam:

- Status codes esperados
- Estrutura de resposta
- Presença de campos obrigatórios
- Tipos de dados corretos

### Debugging de Problemas

#### Erro 401 (Unauthorized)
- Verifique se o token está configurado
- Execute o login novamente
- Confirme que o token não expirou

#### Erro 404 (Not Found)
- Verifique se a baseUrl está correta
- Confirme se o servidor está rodando
- Verifique se os IDs existem no banco

#### Erro 422 (Validation Error)
- Verifique os dados de entrada
- Confirme o formato JSON
- Valide campos obrigatórios

### Logs de Console

Use `console.log()` nos scripts para debug:

```javascript
// No script de teste
console.log("Response:", pm.response.json());
console.log("Token:", pm.environment.get("authToken"));
```

## 📊 Monitoramento e Métricas

### Collection Runner

Use o Collection Runner para:

- Executar testes automatizados
- Gerar relatórios de execução
- Monitorar performance dos endpoints
- Validar regressões

### Exportação de Resultados

1. Execute a coleção via Runner
2. Exporte os resultados em JSON/HTML
3. Use para análise de performance
4. Integre com CI/CD se necessário

## 🔧 Configurações Avançadas

### Variables Dinâmicas

Use Postman's dynamic variables:

```javascript
// Gerar dados aleatórios
{{$randomFirstName}}
{{$randomEmail}}
{{$randomUUID}}
{{$timestamp}}
```

### Environments Múltiplos

Configure environments para:

- **Development**: `http://localhost:8000`
- **Staging**: `https://staging.employeevirtual.com`
- **Production**: `https://api.employeevirtual.com`

### Interceptor Requests

Para debugging avançado, configure:

1. Postman Interceptor
2. Console logs detalhados
3. Network monitoring
4. Request/Response inspection

## 📚 Recursos Adicionais

### Documentação Relacionada

- `ROTEIRO_TESTES_COMPLETO.md`: Guia completo de testes
- `API_DOCUMENTATION.md`: Documentação detalhada da API
- `INSTALLATION.md`: Guia de instalação do projeto

### Scripts de Automação

Para integração com CI/CD:

```bash
# Executar via Newman (CLI)
newman run EmployeeVirtual_Agents_API.postman_collection.json \
  -e environment.json \
  --reporters cli,html \
  --reporter-html-export results.html
```

### Suporte e Troubleshooting

1. Verifique os logs do servidor
2. Confirme a configuração do banco de dados
3. Valide as configurações de CORS
4. Teste endpoints individuais primeiro

---

## ✅ Checklist de Configuração

- [ ] Postman instalado e atualizado
- [ ] Coleção importada com sucesso
- [ ] Ambiente configurado com variáveis corretas
- [ ] Servidor local rodando na porta 8000
- [ ] Banco de dados configurado e populado
- [ ] Credenciais de teste disponíveis
- [ ] Token de autenticação funcionando
- [ ] Primeiro request de teste executado com sucesso

---

**Última atualização**: {{$timestamp}}
**Versão**: 1.0.0
**Autor**: EmployeeVirtual Development Team
