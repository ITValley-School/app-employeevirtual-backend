# Autenticação EmployeeVirtual

## Como Funciona a Autenticação

O sistema utiliza **autenticação baseada em tokens de sessão** com validação automática via **FastAPI Dependencies**.

## Fluxo Completo da Autenticação

### 1. **Registro de Usuário** (`POST /api/auth/register`)

```
📨 DADOS → 🧠 SERVICE → 🔐 HASH SENHA → 💾 REPOSITORY → 🗃️ BANCO
```

**Processo**:
1. **API** recebe dados do usuário
2. **UserService** verifica se email já existe
3. **Hash da senha** com PBKDF2 + salt aleatório
4. **Repository** persiste usuário no banco
5. **Retorna** dados do usuário (sem senha)

**Tecnologia**: `hashlib.pbkdf2_hmac` com salt de 16 bytes e 100.000 iterações

### 2. **Login** (`POST /api/auth/login`)

```
📨 EMAIL/SENHA → 🔍 BUSCA USER → 🔐 VERIFICA SENHA → 🎫 GERA TOKEN → 💾 SESSÃO
```

**Processo**:
1. **API** recebe email e senha
2. **UserService** busca usuário pelo email
3. **Verifica senha** contra hash armazenado
4. **Gera token** único de sessão (32 bytes)
5. **Cria sessão** no banco com expiração (7 dias)
6. **Retorna** token + dados do usuário

**Token**: `secrets.token_urlsafe(32)` (44 caracteres)

### 3. **Validação Automática** (em cada requisição protegida)

```
📨 REQUEST + TOKEN → 🔍 VALIDA SESSÃO → ✅ USER → 🚀 ENDPOINT
```

**Processo**:
1. **Header** `Authorization: Bearer <token>`
2. **Dependency** `get_current_user_dependency()` executa automaticamente
3. **UserService** busca sessão ativa pelo token
4. **Verifica expiração** e status da sessão
5. **Retorna usuário** ou erro 401

## Implementação Técnica

### 🔐 **Hash de Senha** (PBKDF2)
```python
def _hash_password(self, password: str) -> str:
    salt = secrets.token_hex(16)  # Salt aleatório 16 bytes
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{password_hash.hex()}"  # Formato: "salt:hash"

def _verify_password(self, password: str, password_hash: str) -> bool:
    salt, stored_hash = password_hash.split(':')
    password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return password_hash_check.hex() == stored_hash
```

### 🎫 **Geração de Token**
```python
def _generate_session_token(self) -> str:
    return secrets.token_urlsafe(32)  # Token único e seguro
```

### 💾 **Sessão no Banco**
```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 🔍 **Dependency de Autenticação**
```python
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    user_service = UserService(db)
    user = user_service.get_user_by_token(credentials.credentials)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return user
```

## Uso nos Endpoints

### ✅ **Endpoint Protegido**
```python
@router.get("/agents")
async def get_user_agents(
    current_user: UserResponse = Depends(get_current_user_dependency),  # 🔐 Auth obrigatória
    db: Session = Depends(get_db)
):
    # current_user já contém dados do usuário autenticado
    agent_service = AgentService(db)
    return agent_service.get_user_agents(current_user.id)
```

### 🌐 **Endpoint Público**
```python
@router.get("/system-agents")
async def get_system_agents(db: Session = Depends(get_db)):
    # Sem dependency de auth = endpoint público
    agent_service = AgentService(db)
    return agent_service.get_system_agents()
```

## Configuração de Segurança

### ⏰ **Expiração de Sessão**
- **Padrão**: 7 dias (168 horas)
- **Configurável** no método `create_session()`
- **Limpeza automática** de sessões expiradas

### 🔒 **Validação de Token**
```python
def get_session_by_token(self, token: str) -> Optional[UserSession]:
    return self.db.query(UserSession).filter(
        and_(
            UserSession.token == token,           # Token correto
            UserSession.expires_at > datetime.utcnow(),  # Não expirado
            UserSession.is_active == True         # Sessão ativa
        )
    ).first()
```

## Estados da Autenticação

### ✅ **Sucesso**
- **Login**: Retorna token + dados do usuário
- **Request**: Usuario autenticado disponível em `current_user`

### ❌ **Falhas Comuns**

| Situação | Status | Mensagem |
|----------|--------|----------|
| Email não existe | 401 | "Email ou senha incorretos" |
| Senha incorreta | 401 | "Email ou senha incorretos" |
| Token inválido | 401 | "Token inválido ou expirado" |
| Token expirado | 401 | "Token inválido ou expirado" |
| Sem Authorization header | 401 | "Not authenticated" |

## Logout e Invalidação

### 🚪 **Logout** (`POST /api/auth/logout`)
```python
def logout_user(self, token: str) -> bool:
    # Marca sessão como inativa
    session.is_active = False
    return True
```

### 🧹 **Limpeza de Sessões**
```python
def cleanup_expired_sessions(self) -> int:
    # Remove sessões expiradas automaticamente
    expired_sessions = self.db.query(UserSession).filter(
        UserSession.expires_at <= datetime.utcnow()
    ).delete()
    return expired_sessions
```

## Exemplo Prático de Uso

### 🔑 **1. Fazer Login**
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "minhasenha123"
}

# Resposta:
{
  "access_token": "abc123...",
  "token_type": "bearer",
  "expires_at": "2025-01-30T10:00:00",
  "user": { "id": 1, "name": "João", "email": "user@example.com" }
}
```

### 📋 **2. Usar Token em Requisições**
```bash
GET /api/agents
Authorization: Bearer abc123def456ghi789...

# Sistema automaticamente:
# 1. Extrai token do header
# 2. Valida sessão no banco
# 3. Retorna dados do usuário
# 4. Executa endpoint com current_user disponível
```

### 🚪 **3. Fazer Logout**
```bash
POST /api/auth/logout
Authorization: Bearer abc123def456ghi789...

# Resposta:
{
  "message": "Logout realizado com sucesso"
}
```

## Resumo do Fluxo

```
🔐 REGISTRO → Hash senha → Salva user
📝 LOGIN → Valida senha → Gera token → Cria sessão
🎫 REQUEST → Extrai token → Valida sessão → Retorna user
🚪 LOGOUT → Invalida sessão
```

**Vantagens**:
- ✅ Tokens únicos e seguros
- ✅ Sessões com expiração
- ✅ Validação automática via Dependencies
- ✅ Senhas nunca armazenadas em plain text
- ✅ Fácil invalidação de sessões
- ✅ Limpeza automática de sessões expiradas
