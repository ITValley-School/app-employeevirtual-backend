# Roteiro Rápido de Testes - EmployeeVirtual API

## 🚀 Setup Rápido (5 minutos)

### 1. Pré-requisitos
```bash
# 1. Verificar se o servidor está rodando
curl http://localhost:8000/health

# 2. Verificar banco de dados
# Execute o script de validação se necessário
```

### 2. Configurar Postman
1. Importar coleção: `EmployeeVirtual_Agents_API.postman_collection.json`
2. Importar ambiente: `EmployeeVirtual-Development.postman_environment.json`
3. Selecionar ambiente "EmployeeVirtual - Development"

## ⚡ Teste Básico (2 minutos)

### Sequência Mínima de Validação

1. **Health Check**
   ```
   GET /health
   Esperado: 200 OK
   ```

2. **Registro de Usuário**
   ```
   POST /auth/register
   Body: {
     "email": "teste@exemplo.com",
     "password": "senha123",
     "name": "Usuário Teste"
   }
   Esperado: 201 Created
   ```

3. **Login**
   ```
   POST /auth/login
   Body: {
     "email": "teste@exemplo.com",
     "password": "senha123"
   }
   Esperado: 200 OK + token
   ```

4. **Perfil do Usuário**
   ```
   GET /users/me
   Headers: Authorization: Bearer {token}
   Esperado: 200 OK + dados do usuário
   ```

5. **Criar Agente**
   ```
   POST /agents
   Headers: Authorization: Bearer {token}
   Body: {
     "name": "Agente Teste",
     "type": "assistant",
     "description": "Agente para testes"
   }
   Esperado: 201 Created
   ```

## 🧪 Teste Completo (10 minutos)

### Execute na Collection Runner

1. Abra a coleção no Postman
2. Clique em "Run collection"
3. Selecione todos os requests
4. Execute em sequência
5. Verifique se todos passaram

### Resultados Esperados

- ✅ **Autenticação**: 100% de sucesso
- ✅ **Usuários**: 100% de sucesso  
- ✅ **Agentes**: 100% de sucesso
- ✅ **Chats**: 100% de sucesso
- ✅ **Fluxos**: 100% de sucesso
- ✅ **Arquivos**: 100% de sucesso
- ✅ **Dashboard**: 100% de sucesso

## 🔍 Debugging Rápido

### Problemas Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| Connection refused | Servidor não rodando | `python main.py` |
| 401 Unauthorized | Token inválido | Refazer login |
| 422 Validation Error | Dados inválidos | Verificar body |
| 500 Internal Error | Erro no banco | Verificar logs |

### Comandos Úteis

```bash
# Verificar logs do servidor
Get-Content -Tail 20 logs/app.log

# Verificar processo Python
Get-Process python

# Reiniciar servidor
Stop-Process -Name python -Force
python main.py

# Verificar porta 8000
netstat -an | findstr :8000
```

## 📊 Checklist de Validação

### Funcionalidades Core
- [ ] Registro e login funcionando
- [ ] Token JWT sendo gerado
- [ ] Autorização funcionando
- [ ] CRUD de agentes funcionando
- [ ] CRUD de chats funcionando
- [ ] Upload de arquivos funcionando
- [ ] Dashboard retornando dados

### Segurança
- [ ] Endpoints protegidos exigem token
- [ ] Tokens inválidos são rejeitados
- [ ] Usuários só acessam seus próprios dados
- [ ] Validação de entrada funcionando

### Performance
- [ ] Responses < 500ms (desenvolvimento)
- [ ] Sem vazamentos de memória
- [ ] Conexões de banco sendo fechadas
- [ ] Logs sendo gerados corretamente

## 🔧 Comandos de Manutenção

### Reset Completo do Ambiente

```bash
# 1. Parar servidor
Stop-Process -Name python -Force

# 2. Limpar banco (se necessário)
# Execute scripts/database/drop_all_tables_clean.sql

# 3. Recriar schema
# Execute scripts/database/database_schema_super_clean.sql

# 4. Reiniciar servidor
python main.py

# 5. Testar health check
curl http://localhost:8000/health
```

### Verificação de Integridade

```bash
# Verificar arquivos críticos
Test-Path "main.py"
Test-Path "requirements.txt"
Test-Path "scripts/database/database_schema_super_clean.sql"

# Verificar estrutura de pastas
Get-ChildItem -Directory | Select-Object Name
```

## 📈 Próximos Passos

Após validação básica:

1. **Testes de Carga**: Use Newman para testes automatizados
2. **Integração**: Configure CI/CD com os testes
3. **Monitoramento**: Implemente métricas e alertas
4. **Documentação**: Mantenha este roteiro atualizado

---

**Tempo Total**: ~15 minutos
**Última Atualização**: $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Versão**: 1.0.0
