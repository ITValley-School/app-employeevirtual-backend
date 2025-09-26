# ITValley Security SDK - Guia de Integração

## ✅ SDK Instalado e Funcionando

O ITValley Security SDK foi integrado com sucesso ao sistema de autenticação do EmployeeVirtual Backend.

## 🔧 Funcionalidades Implementadas

### 1. Login com SDK (`/auth/login`)
- **Antes**: Usava JWTService manual 
- **Agora**: Usa `itvalleysecurity.issue_pair()`
- **Retorno**: Inclui `access_token`, `refresh_token`, `access_expires_at`, `refresh_expires_at`
- **Cookie**: HttpOnly cookie configurado automaticamente

### 2. Refresh Token com SDK (`/auth/refresh`)
- **Antes**: Validação manual com JWTService
- **Agora**: Usa `itvalleysecurity.verify_refresh()` + `issue_pair()`
- **Validação**: Mais robusta com tratamento de `InvalidToken`

### 3. Dependency Function com SDK (`get_current_user_sdk`)
- **Nova função**: `get_current_user_sdk()` 
- **Validação**: Usa `itvalleysecurity.verify_access()`
- **Uso**: Substitui `get_current_user` em endpoints que precisam do SDK

## 📝 Como Usar

### Exemplo de Login
```bash
# POST /auth/login
{
    "email": "user@example.com",
    "password": "senha123"
}

# Resposta com SDK:
{
    "token_type": "Bearer",
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "access_expires_at": "2025-09-25T22:30:00Z",
    "refresh_expires_at": "2025-10-25T21:30:00Z",
    "user_id": "uuid-do-usuario",
    "email": "user@example.com"
}
```

### Exemplo de Refresh Token
```bash
# POST /auth/refresh
{
    "refresh_token": "eyJ..."
}

# Resposta:
{
    "access_token": "novo_eyJ...",
    "refresh_token": "novo_eyJ...",
    "token_type": "Bearer",
    "access_expires_at": "2025-09-25T22:45:00Z",
    "refresh_expires_at": "2025-10-25T21:45:00Z",
    "user_id": "uuid-do-usuario"
}
```

### Usando a Nova Dependency
```python
# Em qualquer endpoint, substitua:
# current_user: UserResponse = Depends(get_current_user)

# Por:
from api.auth_api import get_current_user_sdk
current_user: UserResponse = Depends(get_current_user_sdk)
```

## 🔍 Funções SDK Disponíveis

1. **`issue_pair(sub, email)`** - Gera access_token e refresh_token
2. **`verify_access(token)`** - Valida access_token 
3. **`verify_refresh(token)`** - Valida refresh_token

## ⚡ Benefícios da Integração

- ✅ **Segurança aprimorada**: SDK especializado em JWT
- ✅ **Menos código**: Não precisa gerenciar JWT manualmente  
- ✅ **Padronização**: Seguindo padrões ITValley
- ✅ **Tratamento de erros**: `InvalidToken` exception específica
- ✅ **Compatibilidade**: Mantém API existente funcionando

## 🚀 Próximos Passos

1. **Migração gradual**: Substituir endpoints um por vez
2. **Testes**: Validar todos os fluxos de autenticação
3. **Configuração**: Ajustar configurações de expiração se necessário
4. **Documentação**: Atualizar API docs com novos campos de resposta

---

**Status**: ✅ Integração Completa  
**Testado**: ✅ Login, Refresh, Validation  
**Branch**: `test_sdk_carlos`  
**Data**: 25 de Setembro, 2025