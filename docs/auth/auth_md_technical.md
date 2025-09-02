# 🔐 auth/ - Sistema de Autenticação JWT

**Documentação técnica da pasta auth/**  
**Sistema:** EmployeeVirtual  
**Versão:** 1.0  

---

## 📁 Estrutura da Pasta

```
auth/
├── config.py        # Configurações e constantes JWT
├── jwt_service.py   # Lógica de criação/validação de tokens
└── dependencies.py  # Dependencies FastAPI para endpoints
```

---

## 📄 config.py

**Responsabilidade:** Configurações centrais e validações

### Configurações principais
```python
JWT_SECRET_KEY          # Chave secreta do .env (obrigatório, 32+ chars)
JWT_ALGORITHM           # Algoritmo JWT (padrão: HS256)
ACCESS_TOKEN_EXPIRE_MINUTES  # Expiração access token (padrão: 15 min)
REFRESH_TOKEN_EXPIRE_DAYS    # Expiração refresh token (padrão: 7 dias)
```

### Configurações de cookies
```python
COOKIE_SECURE    # True para HTTPS, False para desenvolvimento
COOKIE_SAMESITE  # "strict" para CSRF protection
COOKIE_HTTPONLY  # Sempre True (XSS protection)
```

### Constantes de segurança
```python
JWT_ISSUER = "EmployeeVirtual"   # Identificador da aplicação
JWT_TYPE_ACCESS = "access"       # Tipo do access token
JWT_TYPE_REFRESH = "refresh"     # Tipo do refresh token
```

### Mensagens de erro padronizadas
```python
ERROR_MESSAGES = {
    "TOKEN_NOT_PROVIDED": "Token de acesso não fornecido",
    "TOKEN_INVALID": "Token inválido, expirado ou revogado",
    "TOKEN_MALFORMED": "Token malformado",
    "USER_NOT_FOUND": "Usuário não encontrado ou inativo",
    "PREMIUM_REQUIRED": "Este recurso requer plano Premium ou Enterprise",
    "ADMIN_REQUIRED": "Acesso restrito a administradores"
}
```

### Validações automáticas
- Verifica se `JWT_SECRET_KEY` existe e tem 32+ caracteres
- Ajusta configurações de cookie para desenvolvimento
- Valida algoritmo JWT

---

## 🔧 jwt_service.py

**Responsabilidade:** Lógica de tokens JWT (criar, validar, revogar)

### Classe principal: JWTService

#### Métodos públicos
```python
@staticmethod
def create_access_token(user_id: int, email: str) -> str
    """Cria access token (15 min de duração)"""

@staticmethod  
def create_refresh_token(user_id: int) -> str
    """Cria refresh token (7 dias de duração, sem email)"""

@staticmethod
def verify_token(token: str, expected_type: str = "access") -> Optional[Dict]
    """Verifica e decodifica token JWT com validações rigorosas"""

@staticmethod
def blacklist_token(token: str) -> None
    """Adiciona token à blacklist (para logout)"""

@staticmethod
def is_blacklisted(token: str) -> bool
    """Verifica se token está revogado"""

@staticmethod
def extract_user_id(token: str) -> Optional[int]
    """Extrai user_id sem validar expiração (para logs)"""

@staticmethod
def get_token_info(token: str) -> Dict[str, Any]
    """Obtém informações detalhadas do token (para debug)"""
```

#### Método interno
```python
@staticmethod
def _create_token(user_id, email, token_type, expires_minutes, expires_days) -> str
    """Método interno para criação de qualquer tipo de token"""

@staticmethod
def _get_token_hash(token: str) -> str
    """Gera hash SHA256 do token para blacklist (segurança)"""
```

### Claims JWT incluídos
```python
{
    "sub": str(user_id),              # Subject (ID do usuário)
    "email": email,                   # Email (apenas access token)
    "exp": expire_timestamp,          # Expiration time
    "iat": issued_timestamp,          # Issued at
    "nbf": not_before_timestamp,      # Not before
    "jti": unique_token_id,           # JWT ID único
    "type": "access" | "refresh",     # Tipo do token
    "iss": "EmployeeVirtual"          # Issuer
}
```

### Validações de segurança
- ✅ Verificação de assinatura
- ✅ Validação de expiração
- ✅ Validação de issued at
- ✅ Validação de not before
- ✅ Verificação de blacklist
- ✅ Validação de tipo de token
- ✅ Validação de issuer
- ✅ Verificação de idade máxima (24h)

### Funções auxiliares
```python
def create_token_pair(user_id: int, email: str) -> Dict[str, Any]
    """Cria par access + refresh token para login"""

def revoke_token_pair(access_token: str, refresh_token: str) -> None
    """Revoga ambos os tokens para logout"""
```

### Blacklist de tokens
- Implementação em memória para desenvolvimento
- Hash SHA256 dos tokens (não armazena token completo)
- Em produção: usar Redis com TTL automático

---

## 🔒 dependencies.py

**Responsabilidade:** Dependencies FastAPI para proteção de endpoints

### Dependencies principais

#### get_current_user()
```python
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse
```
- **Uso:** Proteção básica de endpoints
- **Extrai token de:** Authorization header OU HttpOnly cookie
- **Valida:** Token JWT + busca usuário no banco
- **Retorna:** UserResponse completo
- **Exceções:** 401 se token inválido/ausente

#### get_current_user_optional()
```python
async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserResponse]
```
- **Uso:** Endpoints que funcionam com ou sem autenticação
- **Retorna:** UserResponse se autenticado, None se não
- **Não levanta exceção** se token ausente

#### require_premium_user()
```python
async def require_premium_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse
```
- **Uso:** Endpoints exclusivos para usuários premium
- **Valida:** Se `user.plan` está em `["premium", "enterprise", "admin"]`
- **Exceções:** 402 Payment Required se plano insuficiente

#### require_admin_user()
```python
async def require_admin_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse
```
- **Uso:** Endpoints administrativos
- **Valida:** Se `user.is_admin == True` OU `user.plan == "admin"`
- **Exceções:** 403 Forbidden se não for admin

### Funções utilitárias

#### get_client_ip()
```python
def get_client_ip(request: Request) -> str
```
- Extrai IP real considerando proxies
- Headers verificados: X-Forwarded-For, X-Real-IP
- Fallback: request.client.host

#### extract_token_from_request()
```python
def extract_token_from_request(
    request: Request, 
    credentials: Optional[HTTPAuthorizationCredentials]
) -> Optional[str]
```
- Prioridade 1: Authorization header (Bearer token)
- Prioridade 2: HttpOnly cookie (access_token)
- Retorna None se nenhum encontrado

#### verify_token_only()
```python
async def verify_token_only(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]
```
- **Uso:** Quando só precisa validar token, sem carregar usuário
- **Retorna:** Payload do token (user_id, email, etc.)
- **Performance:** Mais rápido que get_current_user

### Configuração FastAPI Security
```python
security = HTTPBearer(auto_error=False)
```
- `auto_error=False`: Permite handling customizado de erros
- Suporta Authorization header com Bearer token

---

## 🔄 Fluxos de Funcionamento

### Fluxo de Login
1. `POST /api/auth/login` recebe email/senha
2. `UserService.authenticate_user_basic()` valida credenciais
3. `create_token_pair()` gera access + refresh tokens
4. Response define cookies HttpOnly com tokens
5. Cliente recebe confirmação de login

### Fluxo de Request Protegido
1. Cliente faz request com cookie OU Authorization header
2. `get_current_user()` dependency é executada:
   - Extrai token do request
   - `JWTService.verify_token()` valida token
   - Busca usuário no banco
   - Retorna UserResponse
3. Endpoint recebe usuário já validado

### Fluxo de Logout
1. `POST /api/auth/logout` com token atual
2. `JWTService.blacklist_token()` revoga token
3. Response limpa cookies
4. Token fica inutilizável imediatamente

### Fluxo de Refresh
1. Access token expira (15 min)
2. `POST /api/auth/refresh` com refresh token
3. `JWTService.verify_token(refresh_token)` valida
4. Gera novo access token
5. Atualiza cookie com novo token

---

## 🛡️ Medidas de Segurança

### Proteção contra XSS
- **HttpOnly cookies:** JavaScript não acessa tokens
- **Secure cookies:** Apenas HTTPS (produção)
- **Path restriction:** Refresh token só em `/api/auth/refresh`

### Proteção contra CSRF
- **SameSite=Strict:** Navegador só envia de mesmo site
- **Origin validation:** Possível adicionar se necessário

### Proteção contra Token Replay
- **Expiração curta:** 15 minutos para access token
- **Token blacklist:** Revogação imediata
- **JTI único:** Cada token tem ID único

### Proteção contra Token Forgery
- **Assinatura HMAC:** HS256 com chave secreta forte
- **Validação rigorosa:** Todos os claims obrigatórios
- **Issuer validation:** Apenas tokens do EmployeeVirtual
- **Algoritmo fixo:** Não aceita `alg=none`

### Proteção contra Timing Attacks
- **Hashing consistente:** SHA256 para blacklist
- **Error handling uniforme:** Mesma resposta para erros diferentes

---

## 📊 Performance e Escalabilidade

### Vantagens
- **Stateless:** Não consulta banco para validar token
- **Cache-friendly:** Tokens podem ser cached
- **Horizontal scaling:** Funciona com múltiplos servidores
- **Load balancer friendly:** Não precisa sticky sessions

### Considerações para produção
- **Blacklist em Redis:** Para escalabilidade
- **Token rotation:** Refresh tokens rotativos
- **Monitoring:** Logs de tokens inválidos/expirados
- **Rate limiting:** Na infraestrutura (nginx)

---

## 🔧 Extensibilidade

### Adicionando nova dependency
```python
# Em dependencies.py
async def require_enterprise_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if current_user.plan != "enterprise":
        raise HTTPException(status_code=402, detail="Enterprise required")
    return current_user

# Uso no endpoint
@router.post("/enterprise-feature")
async def enterprise_feature(user = Depends(require_enterprise_user)):
    pass
```

### Adicionando claims customizados
```python
# Em jwt_service.py, método _create_token
payload.update({
    "custom_claim": custom_value,
    "permissions": user_permissions
})
```

### Adicionando validações customizadas
```python
# Em jwt_service.py, método verify_token
if payload.get("custom_claim") != expected_value:
    return None
```

---

## 🐛 Debug e Monitoramento

### Logs importantes
- Login bem-sucedido
- Token expirado
- Token inválido  
- Tentativas de token forjado
- Acesso negado por permissões

### Métricas úteis
- Taxa de tokens expirados
- Frequência de refresh
- Tentativas de login falhadas
- Tokens na blacklist

### Endpoints de debug
- `GET /api/auth/token-info`: Analisa token atual
- `GET /api/auth/security-info`: Status das proteções

---

## 📝 Manutenção

### Rotação de chaves
1. Gerar nova `JWT_SECRET_KEY`
2. Atualizar `.env` 
3. Restart da aplicação
4. Todos os tokens existentes ficam inválidos
5. Usuários precisam fazer novo login

### Limpeza de blacklist
- Tokens expirados podem ser removidos da blacklist
- Em produção: TTL automático no Redis
- Desenvolvimento: Blacklist persiste até restart

### Atualizações de segurança
- Monitorar vulnerabilidades em PyJWT
- Atualizar dependências regularmente
- Revisar configurações de produção

---

**Documentação atualizada:** Julho 2025  
**Próxima revisão:** Agosto 2025  
**Responsável:** Equipe de Desenvolvimento