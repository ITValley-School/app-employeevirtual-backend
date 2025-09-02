# Postman Collection - EmployeeVirtual API

Este diretório contém todos os arquivos necessários para testar a API do EmployeeVirtual usando o Postman.

## 📁 Arquivos Incluídos

### Coleção Principal
- **`EmployeeVirtual_Agents_API.postman_collection.json`**
  - Coleção completa com todos os endpoints da API
  - Inclui scripts de teste automáticos
  - Configurada para extrair e armazenar tokens/IDs automaticamente

### Ambientes
- **`EmployeeVirtual-Development.postman_environment.json`**
  - Ambiente pré-configurado para desenvolvimento local
  - Base URL: `http://localhost:8000`
  - Credenciais de teste incluídas

- **`EmployeeVirtual-Production.postman_environment.json`**
  - Ambiente para produção (credenciais vazias por segurança)
  - Base URL: `https://api.employeevirtual.com`
  - Configurar credenciais manualmente

### Documentação
- **`POSTMAN_SETUP_GUIDE.md`**
  - Guia completo de configuração e uso
  - Instruções detalhadas de setup
  - Troubleshooting e debugging

## 🚀 Setup Rápido

### 1. Importar no Postman
```
1. Abra o Postman
2. File > Import
3. Selecione todos os arquivos .json desta pasta
4. Confirme a importação
```

### 2. Configurar Ambiente
```
1. Selecione "EmployeeVirtual - Development" no dropdown de ambientes
2. Verifique se baseUrl = http://localhost:8000
3. Certifique-se de que o servidor está rodando
```

### 3. Testar Conexão
```
1. Execute: Health Check (GET /health)
2. Deve retornar: 200 OK
3. Se falhar, verifique se o servidor está rodando
```

## 🧪 Executando Testes

### Teste Individual
1. Selecione um request
2. Clique em "Send"
3. Verifique response e testes automáticos

### Teste em Lote
1. Clique na coleção > "Run collection"
2. Selecione ambiente apropriado
3. Execute todos os requests
4. Analise resultados no runner

## 📊 Estrutura da Coleção

```
🔐 Autenticação
├── Login
├── Register
└── Refresh Token

👤 Usuários
├── Get Profile
├── Update Profile
└── Delete Account

🤖 Agentes
├── Create Agent
├── List Agents
├── Get Agent
├── Update Agent
└── Delete Agent

💬 Chats
├── Create Chat
├── List Chats
├── Get Chat
├── Send Message
└── Get Messages

🔄 Fluxos
├── Create Flow
├── List Flows
├── Get Flow
├── Update Flow
└── Delete Flow

📁 Arquivos
├── Upload File
├── List Files
├── Get File
└── Delete File

📊 Dashboard
├── Get Stats
└── Recent Activity
```

## 🔧 Scripts Automáticos

### Token Management
- Extrai token automaticamente após login
- Armazena em variável de coleção
- Aplica automaticamente a requests protegidos

### ID Extraction
- Extrai IDs de responses automaticamente
- Armazena para uso em requests dependentes
- Permite execução em sequência

### Response Validation
- Valida status codes
- Verifica estrutura de response
- Testa tipos de dados

## 🆘 Troubleshooting

### Problemas Comuns

| Problema | Solução |
|----------|---------|
| Connection refused | Servidor não está rodando |
| 401 Unauthorized | Token inválido ou expirado |
| 404 Not Found | Endpoint incorreto ou ID inválido |
| 422 Validation Error | Dados de entrada inválidos |

### Debug Steps
1. Verificar se servidor está rodando: `curl http://localhost:8000/health`
2. Verificar ambiente selecionado no Postman
3. Conferir variáveis de ambiente (baseUrl, authToken)
4. Executar login novamente se 401
5. Verificar logs do servidor para erros internos

## 📚 Recursos Adicionais

- **Guia Completo**: `../ROTEIRO_TESTES_COMPLETO.md`
- **Guia Rápido**: `../QUICK_TEST_GUIDE.md`
- **API Docs**: `../../api/API_DOCUMENTATION.md`
- **Setup**: `../../INSTALLATION.md`

## 🔄 Atualizações

Para manter a coleção atualizada:

1. **Novos Endpoints**: Adicione requests conforme necessário
2. **Mudanças na API**: Atualize URLs e estruturas de dados
3. **Novos Testes**: Adicione validações nos scripts
4. **Ambientes**: Mantenha URLs e credenciais atualizadas

---

**Última Atualização**: 2024-01-01
**Versão da Coleção**: 1.0.0
**Compatibilidade**: Postman 10.x+
