# Arquitetura EmployeeVirtual

## Visão Geral

O EmployeeVirtual é uma aplicação FastAPI que implementa uma **arquitetura em camadas (Layered Architecture)** seguindo os princípios de **Separação de Responsabilidades** e **Inversão de Dependência**. A aplicação é estruturada em 5 camadas principais que se comunicam de forma unidirecional.

## Estrutura das Camadas

```
┌─────────────────────────────────────────────────────────┐
│                    1. API LAYER                        │
│               (Controllers/Endpoints)                  │
│                  FastAPI Routers                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                2. MIDDLEWARE LAYER                     │
│              (Auth, CORS, Logging)                     │
│              Interceptação/Validação                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                3. SERVICE LAYER                        │
│              (Business Logic)                          │
│           Orquestração e Regras de Negócio             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               4. REPOSITORY LAYER                      │
│              (Data Access Layer)                       │
│            Acesso e Persistência de Dados              │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 5. MODEL LAYER                         │
│            (Entities/Data Models)                      │
│         SQLAlchemy Models + Pydantic Schemas           │
└─────────────────────────────────────────────────────────┘
```

## Fluxo de Execução Detalhado

### 1. **API LAYER** (`/api/`)
**Responsabilidade**: Controladores e endpoints HTTP

**Localização**: `api/agent_api.py`, `api/auth_api.py`, `api/chat_api.py`, etc.

**O que faz**:
- Recebe requisições HTTP
- Valida parâmetros de entrada
- Aplica autenticação via dependency injection
- Chama a camada de serviço
- Formata e retorna respostas HTTP

**Exemplo de fluxo**:
```python
# api/agent_api.py
@router.get("/", response_model=List[AgentResponse])
async def get_user_agents(
    include_system: bool = True,
    current_user: UserResponse = Depends(get_current_user_dependency),  # 🔐 Autenticação
    db: Session = Depends(get_db)
):
    agent_service = AgentService(db)  # 📞 Chama Service Layer
    agents = agent_service.get_user_agents(current_user.id, include_system)
    return agents  # 📤 Retorna resposta formatada
```

### 2. **MIDDLEWARE LAYER** (`/middlewares/`)
**Responsabilidade**: Interceptação e validação transversal

**Localização**: `middlewares/auth_middleware.py`, `middlewares/cors_middleware.py`, `middlewares/logging_middleware.py`

**O que faz**:
- **Autenticação**: Valida tokens JWT
- **CORS**: Configura políticas de cross-origin
- **Logging**: Registra requisições e respostas
- **Validação**: Intercepta e valida dados

**Fluxo de Autenticação**:
```python
# api/auth_api.py - Dependency de autenticação
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    user_service = UserService(db)
    user = user_service.get_user_by_token(credentials.credentials)  # 🔍 Valida token
    
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return user  # ✅ Usuário autenticado
```

### 3. **SERVICE LAYER** (`/services/`)
**Responsabilidade**: Lógica de negócio e orquestração

**Localização**: `services/agent_service.py`, `services/user_service.py`, `services/chat_service.py`, etc.

**O que faz**:
- Implementa regras de negócio
- Orquestra chamadas entre repositórios
- Processa e transforma dados
- Gerencia transações complexas
- **NÃO faz consultas SQL diretas**

**Exemplo de orquestração**:
```python
# services/agent_service.py
class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AgentRepository(db)        # 📞 Injeta Repository
        self.user_repository = UserRepository(db)    # 📞 Injeta User Repository
    
    def create_agent(self, user_id: int, agent_data: AgentCreate) -> AgentResponse:
        # 🧠 Lógica de negócio: preparar dados
        agent_dict = {
            "user_id": user_id,
            "name": agent_data.name,
            "description": agent_data.description,
            # ... mais campos
        }
        
        # 📞 Delega para Repository
        agent = self.repository.create_agent(agent_dict)
        
        # 🔄 Transforma em response model
        return AgentResponse.from_orm(agent)
```

### 4. **REPOSITORY LAYER** (`/data/`)
**Responsabilidade**: Acesso exclusivo a dados

**Localização**: `data/agent_repository.py`, `data/user_repository.py`, `data/chat_repository.py`, etc.

**O que faz**:
- Executa consultas SQL (SQLAlchemy)
- Operações CRUD básicas
- Consultas específicas do domínio
- **SEM lógica de negócio**
- Abstrai detalhes do banco de dados

**Exemplo de acesso a dados**:
```python
# data/agent_repository.py
class AgentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_agent(self, agent_data: Dict[str, Any]) -> Agent:
        """Apenas persiste dados - sem lógica de negócio"""
        db_agent = Agent(**agent_data)  # 🏗️ Cria entidade
        self.db.add(db_agent)           # 💾 Persiste
        self.db.commit()                # ✅ Confirma
        self.db.refresh(db_agent)       # 🔄 Atualiza
        return db_agent                 # 📤 Retorna entidade
    
    def get_user_agents(self, user_id: int, include_system: bool = True) -> List[Agent]:
        """Consulta específica do domínio"""
        query = self.db.query(Agent).filter(Agent.user_id == user_id)
        
        if include_system:
            # 🔍 Lógica de consulta complexa
            query = query.filter(
                or_(Agent.user_id == user_id, Agent.agent_type == "system")
            )
        
        return query.all()  # 📋 Retorna lista de entidades
```

### 5. **MODEL LAYER** (`/models/`)
**Responsabilidade**: Definição de estruturas de dados

**Localização**: `models/agent_models.py`, `models/user_models.py`, `models/chat_models.py`, etc.

**O que faz**:
- **SQLAlchemy Models**: Mapeamento objeto-relacional (tabelas)
- **Pydantic Schemas**: Validação e serialização de dados
- **Enums**: Constantes e tipos controlados
- Relacionamentos entre entidades

**Exemplo de modelos**:
```python
# models/agent_models.py

# 🗃️ SQLAlchemy Model (Banco de dados)
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    agent_type = Column(SQLEnum(AgentType), default=AgentType.CUSTOM)
    # ... mais campos

# 📋 Pydantic Schemas (API)
class AgentCreate(BaseModel):
    """Schema para criação de agente"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    agent_type: AgentType = Field(default=AgentType.CUSTOM)

class AgentResponse(BaseModel):
    """Schema para resposta da API"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True  # Permite from_orm()
```

## Fluxo Completo de uma Requisição

### Exemplo: `GET /api/agents/` (Listar agentes do usuário)

```
📨 1. CLIENT REQUEST
   │
   │ GET /api/agents/?include_system=true
   │ Authorization: Bearer <token>
   │
   ▼
🌐 2. API LAYER (agent_api.py)
   │ 
   │ @router.get("/", response_model=List[AgentResponse])
   │ async def get_user_agents(...)
   │
   ▼
🔐 3. MIDDLEWARE (auth via dependency)
   │
   │ get_current_user_dependency()
   │ ├─ Valida token JWT
   │ ├─ UserService.get_user_by_token()
   │ └─ Retorna UserResponse ou HTTPException(401)
   │
   ▼
🧠 4. SERVICE LAYER (agent_service.py)
   │
   │ AgentService.get_user_agents(user_id, include_system)
   │ ├─ Aplica regras de negócio
   │ ├─ Valida parâmetros
   │ └─ Chama repository
   │
   ▼
💾 5. REPOSITORY LAYER (agent_repository.py)
   │
   │ AgentRepository.get_user_agents(user_id, include_system)
   │ ├─ Monta query SQL
   │ ├─ Executa consulta no banco
   │ └─ Retorna List[Agent]
   │
   ▼
🗃️ 6. MODEL LAYER (agent_models.py)
   │
   │ Agent (SQLAlchemy Model)
   │ ├─ Mapeia dados do banco
   │ └─ Relacionamentos (User, AgentKnowledge, etc.)
   │
   ▼
🔄 7. TRANSFORMAÇÃO (service.py)
   │
   │ List[Agent] → List[AgentResponse]
   │ ├─ Serialização Pydantic
   │ └─ Formatação para API
   │
   ▼
📤 8. API RESPONSE
   │
   │ HTTP 200 OK
   │ Content-Type: application/json
   │ [{"id": 1, "name": "Agent1", ...}, ...]
```

## Vantagens da Arquitetura

### 🔒 **Separação de Responsabilidades**
- Cada camada tem uma responsabilidade específica
- Facilita manutenção e teste
- Reduz acoplamento entre componentes

### 🧪 **Testabilidade**
- Camadas podem ser testadas independentemente
- Fácil mock de dependências
- Testes unitários e de integração separados

### 🔄 **Flexibilidade**
- Mudanças em uma camada não afetam outras
- Fácil substituição de implementações
- Suporte a diferentes provedores (banco, LLM, etc.)

### 📈 **Escalabilidade**
- Services podem ser distribuídos
- Repositórios suportam diferentes bancos
- APIs podem ser versionadas independentemente

## Padrões de Design Utilizados

### 🏭 **Repository Pattern**
- Abstrai acesso a dados
- Facilita mudança de banco de dados
- Melhora testabilidade com mocks

### 💉 **Dependency Injection**
- FastAPI Depends() para injeção automática
- Facilita configuração e testes
- Reduz acoplamento entre camadas

### 🎯 **Single Responsibility Principle**
- Cada classe tem uma responsabilidade
- Facilita manutenção e extensão
- Código mais limpo e organizado

### 🔗 **Chain of Responsibility**
- Middlewares processam requisições em cadeia
- Flexível para adicionar/remover interceptadores
- Separação de concerns transversais

## Configuração e Inicialização

### 🚀 **Inicialização da Aplicação** (`main.py`)
```python
# 1. Criar aplicação FastAPI
app = FastAPI(title="EmployeeVirtual API", ...)

# 2. Configurar middlewares
add_cors_middleware(app)

# 3. Registrar routers automaticamente
register_routers(app)
```

### 🔧 **Configuração de Routers** (`api/router_config.py`)
```python
ROUTER_CONFIG = [
    {"router": auth_router, "prefix": "/api/auth", "tags": ["Autenticação"]},
    {"router": agent_router, "prefix": "/api/agents", "tags": ["Agentes"]},
    # ... outros routers
]
```

### 🗄️ **Configuração de Banco** (`data/database.py`)
```python
# Configuração SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Dependency para sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Considerações de Segurança

### 🔐 **Autenticação JWT**
- Tokens com expiração configurável
- Validação em cada endpoint protegido
- Refresh tokens para sessões longas

### 🛡️ **Autorização por Recurso**
- Verificação de ownership nos services
- Usuários só acessam seus próprios dados
- Agentes do sistema disponíveis para todos

### 🌐 **CORS e Middleware**
- Configuração flexível de origins
- Headers de segurança
- Logging de requisições para auditoria

## Como Estender a Arquitetura

### 📄 **Adicionando Nova Entidade** (ex: "Projects")
1. **Model**: Criar `models/project_models.py`
2. **Repository**: Criar `data/project_repository.py`
3. **Service**: Criar `services/project_service.py`
4. **API**: Criar `api/project_api.py`
5. **Router**: Adicionar em `router_config.py`

### 🔌 **Adicionando Novo Provider** (ex: Nova LLM)
1. **Enum**: Adicionar em `models/agent_models.py`
2. **Service**: Implementar lógica em `services/agent_service.py`
3. **Repository**: Adicionar queries se necessário

### 🛠️ **Adicionando Middleware**
1. Criar arquivo em `middlewares/`
2. Implementar classe base `BaseHTTPMiddleware`
3. Adicionar no `main.py`

## Monitoramento e Observabilidade

### 📊 **Logs Estruturados**
- Logging middleware para todas as requisições
- Logs de erro detalhados em cada camada
- Correlação de IDs para rastreamento

### 📈 **Métricas de Performance**
- Tempo de resposta por endpoint
- Queries de banco de dados mais lentas
- Usage de recursos por usuário

### 🔍 **Debug e Troubleshooting**
- Stack traces completos
- Logs de SQL queries em desenvolvimento
- Health checks de dependências externas

---

## Resumo do Fluxo de Dados

```
📨 REQUEST → 🌐 API → 🔐 AUTH → 🧠 SERVICE → 💾 REPOSITORY → 🗃️ MODEL
                                     ↓
📤 RESPONSE ← 🌐 API ← 🔄 TRANSFORM ← 🧠 SERVICE ← 💾 REPOSITORY ← 🗃️ MODEL
```

Esta arquitetura garante **separação clara de responsabilidades**, **facilidade de manutenção**, **testabilidade** e **escalabilidade** para o sistema EmployeeVirtual.
