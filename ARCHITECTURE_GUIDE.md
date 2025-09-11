# 🏗️ Guia de Arquitetura Clean Code & DDD - EmployeeVirtual

## 📋 Índice
1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Princípios Fundamentais](#princípios-fundamentais)
3. [Estrutura de Camadas](#estrutura-de-camadas)
4. [Padrões de Código](#padrões-de-código)
5. [Responsabilidade Única](#responsabilidade-única)
6. [Injeção de Dependência](#injeção-de-dependência)
7. [Exemplos Práticos](#exemplos-práticos)
8. [Checklist para Revisão](#checklist-para-revisão)

---

## 🎯 Visão Geral da Arquitetura

Nossa aplicação segue os princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**, organizando o código em camadas bem definidas com responsabilidades claras.

### Estrutura Atual:
```
employeevirtual/
├── api/                    # 🌐 Camada de Apresentação (Controllers)
├── services/               # 🔧 Camada de Aplicação (Business Logic)
├── data/                   # 💾 Camada de Infraestrutura (Repositories)
├── models/                 # 📄 Camada de Domínio (Entities/DTOs)
├── dependencies/           # 🔌 Injeção de Dependências
├── auth/                   # 🔐 Autenticação e Autorização
└── middlewares/            # 🔄 Interceptadores e Filtros
```

---

## 🎭 Princípios Fundamentais

### 1. **Single Responsibility Principle (SRP)**
> **"Uma classe deve ter apenas um motivo para mudar"**

✅ **CORRETO:**
```python
class UserService:
    """Responsável APENAS pela lógica de negócio de usuários"""
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        # Validações de negócio
        # Regras específicas de usuário
        pass
```

❌ **INCORRETO:**
```python
class UserService:
    """Faz muitas coisas - VIOLA SRP"""
    
    def create_user(self, user_data: UserCreate):
        pass
    
    def send_email(self, email: str):  # ❌ Responsabilidade de email
        pass
    
    def generate_report(self):  # ❌ Responsabilidade de relatório
        pass
```

### 2. **Dependency Inversion Principle (DIP)**
> **"Dependa de abstrações, não de implementações"**

✅ **CORRETO:**
```python
# API depende da abstração (Service)
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)  # ✅ Injeção
):
    return user_service.create_user(user_data)
```

❌ **INCORRETO:**
```python
# API depende da implementação (Database)
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)  # ❌ Dependência direta
):
    user = User(**user_data.dict())  # ❌ Lógica no controller
    db.add(user)
    db.commit()
```

---

## 🏛️ Estrutura de Camadas

### 🌐 Camada API (Controllers)
**Responsabilidade:** Receber requisições HTTP, validar entrada, chamar services e retornar respostas.

```python
# api/user_api.py
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    ✅ Responsabilidades CORRETAS:
    - Receber dados HTTP
    - Validar autenticação
    - Chamar service
    - Retornar resposta HTTP
    """
    try:
        return user_service.create_user(user_data, current_user.id)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**❌ NÃO FAÇA na camada API:**
- Lógica de negócio
- Acesso direto ao banco de dados
- Validações complexas
- Transformações de dados

### 🔧 Camada Service (Business Logic)
**Responsabilidade:** Implementar regras de negócio, orquestrar operações e coordenar repositories.

```python
# services/user_service.py
class UserService:
    """Serviço para lógica de negócio de usuários"""
    
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.email_service = EmailService()  # Dependência externa
    
    def create_user(self, user_data: UserCreate, created_by_id: int) -> UserResponse:
        """
        ✅ Responsabilidades CORRETAS:
        - Validações de negócio
        - Regras de domínio
        - Orquestração de repositories
        - Transformação de dados
        """
        # Validação de negócio
        if self.user_repository.email_exists(user_data.email):
            raise BusinessException("Email já existe")
        
        # Regra de negócio
        user_data.password = self._hash_password(user_data.password)
        
        # Orquestração
        user = self.user_repository.create(user_data)
        self.email_service.send_welcome_email(user.email)
        
        return UserResponse.from_entity(user)
```

**❌ NÃO FAÇA na camada Service:**
- Acesso direto ao banco (use repositories)
- Lógica de apresentação (HTTP, JSON, etc.)
- Detalhes de infraestrutura

### 💾 Camada Repository (Data Access)
**Responsabilidade:** Acesso aos dados, queries e persistência.

```python
# data/user_repository.py
class UserRepository:
    """Repository para acesso aos dados de usuários"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_data: UserCreate) -> UserEntity:
        """
        ✅ Responsabilidades CORRETAS:
        - Queries ao banco
        - Mapeamento ORM
        - Persistência
        """
        user_entity = UserEntity(**user_data.dict())
        self.db.add(user_entity)
        self.db.commit()
        self.db.refresh(user_entity)
        return user_entity
    
    def find_by_email(self, email: str) -> Optional[UserEntity]:
        return self.db.query(UserEntity).filter(
            UserEntity.email == email
        ).first()
```

**❌ NÃO FAÇA na camada Repository:**
- Lógica de negócio
- Validações complexas
- Transformações de dados de negócio

### 📄 Camada Models (Domain)
**Responsabilidade:** Definir estruturas de dados, DTOs e entidades.

```python
# models/user_models.py
class UserCreate(BaseModel):
    """DTO para criação de usuário"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    """DTO para resposta de usuário"""
    id: int
    name: str
    email: str
    created_at: datetime
    
    @classmethod
    def from_entity(cls, entity: UserEntity) -> "UserResponse":
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            created_at=entity.created_at
        )
```

---

## 🔌 Injeção de Dependência

### Service Providers
Centralize a criação de services em `dependencies/service_providers.py`:

```python
# dependencies/service_providers.py
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Provedor do UserService
    
    ✅ Vantagens:
    - Centralização da criação
    - Facilita testes (mocking)
    - Gerenciamento de dependências
    """
    return UserService(db)
```

### Uso nos Controllers
```python
# api/user_api.py
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)  # ✅ Injeção
):
    return user_service.create_user(user_data)
```

---

## 🎯 Responsabilidade Única por Camada

### 📋 Checklist de Responsabilidades

#### API Layer ✅
- [ ] Recebe requisições HTTP
- [ ] Valida entrada básica (tipos, formatos)
- [ ] Chama services apropriados
- [ ] Retorna respostas HTTP
- [ ] Trata exceções HTTP

#### Service Layer ✅
- [ ] Implementa regras de negócio
- [ ] Valida dados de domínio
- [ ] Orquestra repositories
- [ ] Transforma dados
- [ ] Gerencia transações

#### Repository Layer ✅
- [ ] Acessa banco de dados
- [ ] Executa queries
- [ ] Mapeia ORM para entidades
- [ ] Persiste dados

#### Model Layer ✅
- [ ] Define estruturas de dados
- [ ] Valida tipos e formatos
- [ ] Serializa/deserializa

---

## 📚 Exemplos Práticos

### Exemplo Completo: Criar Agente

#### 1. Controller (API)
```python
# api/agent_api.py
@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """Criar novo agente - Responsabilidade: HTTP handling"""
    try:
        return agent_service.create_agent(agent_data, current_user.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 2. Service (Business Logic)
```python
# services/agent_service.py
class AgentService:
    def __init__(self, db: Session):
        self.agent_repository = AgentRepository(db)
        self.user_repository = UserRepository(db)
    
    def create_agent(self, agent_data: AgentCreate, user_id: int) -> AgentResponse:
        """Criar agente - Responsabilidade: Business rules"""
        
        # Validação de negócio
        user = self.user_repository.find_by_id(user_id)
        if not user.can_create_agent():
            raise BusinessException("Usuário não pode criar agentes")
        
        # Regra de negócio: limite de agentes
        agent_count = self.agent_repository.count_by_user(user_id)
        if agent_count >= user.plan.max_agents:
            raise BusinessException("Limite de agentes atingido")
        
        # Criação
        agent = self.agent_repository.create(agent_data, user_id)
        
        return AgentResponse.from_entity(agent)
```

#### 3. Repository (Data Access)
```python
# data/agent_repository.py
class AgentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, agent_data: AgentCreate, user_id: int) -> AgentEntity:
        """Criar agente - Responsabilidade: Data persistence"""
        agent = AgentEntity(
            name=agent_data.name,
            description=agent_data.description,
            user_id=user_id,
            created_at=datetime.now()
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def count_by_user(self, user_id: int) -> int:
        """Contar agentes do usuário"""
        return self.db.query(AgentEntity).filter(
            AgentEntity.user_id == user_id
        ).count()
```

#### 4. Models (Data Structures)
```python
# models/agent_models.py
class AgentCreate(BaseModel):
    """DTO para criação de agente"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class AgentResponse(BaseModel):
    """DTO para resposta de agente"""
    id: int
    name: str
    description: Optional[str]
    user_id: int
    created_at: datetime
    
    @classmethod
    def from_entity(cls, entity: AgentEntity) -> "AgentResponse":
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            user_id=entity.user_id,
            created_at=entity.created_at
        )
```

---

## ✅ Checklist para Revisão de Código

### 🔍 Code Review Checklist

#### Arquitetura ✅
- [ ] Cada classe tem uma única responsabilidade?
- [ ] As dependências estão sendo injetadas?
- [ ] As camadas estão bem separadas?
- [ ] Não há vazamento de responsabilidades?

#### API Layer ✅
- [ ] Controller apenas chama services?
- [ ] Não há lógica de negócio no controller?
- [ ] Tratamento de exceções adequado?
- [ ] Response models corretos?

#### Service Layer ✅
- [ ] Contém apenas lógica de negócio?
- [ ] Usa repositories para acesso a dados?
- [ ] Validações de domínio presentes?
- [ ] Transações gerenciadas adequadamente?

#### Repository Layer ✅
- [ ] Apenas acesso a dados?
- [ ] Queries otimizadas?
- [ ] Mapeamento ORM correto?
- [ ] Sem lógica de negócio?

#### Models ✅
- [ ] DTOs bem definidos?
- [ ] Validações de tipos?
- [ ] Métodos de transformação presentes?
- [ ] Sem lógica de negócio?

---

## 🚨 Anti-Patterns (O que NÃO fazer)

### ❌ God Class
```python
# ❌ EVITE: Classe que faz tudo
class UserController:
    def create_user(self):
        # Lógica HTTP ✅
        # Lógica de negócio ❌
        # Acesso ao banco ❌
        # Envio de email ❌
        # Geração de relatório ❌
        pass
```

### ❌ Anemic Domain Model
```python
# ❌ EVITE: Modelos sem comportamento
class User:
    name: str
    email: str
    # Sem métodos de negócio ❌

# ✅ PREFIRA: Modelos com comportamento
class User:
    name: str
    email: str
    
    def can_create_agent(self) -> bool:
        return self.plan.allows_agents
```

### ❌ Tight Coupling
```python
# ❌ EVITE: Dependência direta
class UserService:
    def __init__(self):
        self.db = Database()  # ❌ Acoplamento forte

# ✅ PREFIRA: Injeção de dependência
class UserService:
    def __init__(self, db: Session):  # ✅ Inversão de dependência
        self.user_repository = UserRepository(db)
```

---

## 🎓 Diretrizes para IA/Copilot

### Prompts Recomendados

```
"Crie um [controller/service/repository] seguindo a arquitetura clean 
do projeto EmployeeVirtual, respeitando o princípio de responsabilidade 
única e usando injeção de dependência."
```

```
"Refatore este código para seguir os padrões de clean architecture 
definidos no ARCHITECTURE_GUIDE.md, separando as responsabilidades 
em camadas adequadas."
```

### Validação Automática
Sempre pergunte à IA:
1. "Esta classe tem apenas uma responsabilidade?"
2. "As dependências estão sendo injetadas corretamente?"
3. "Há vazamento de responsabilidades entre camadas?"
4. "O código segue os padrões do ARCHITECTURE_GUIDE.md?"

---

## 📖 Recursos Adicionais

### Leituras Recomendadas
- [Clean Architecture - Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

### Ferramentas
- **Linting:** Configurar pylint/flake8 para validar estrutura
- **Testing:** Criar testes unitários por camada
- **Documentation:** Manter docstrings atualizadas

---

## 🎯 Conclusão

Este guia deve ser a **fonte da verdade** para todos os desenvolvedores e IAs que trabalham no projeto EmployeeVirtual. 

**Lembre-se:**
- **Clean Code** = Código fácil de ler, entender e modificar
- **DDD** = Foco no domínio e regras de negócio
- **Single Responsibility** = Uma classe, uma responsabilidade
- **Dependency Injection** = Inversão de controle e baixo acoplamento

Mantenha este documento atualizado conforme a arquitetura evolui! 🚀

---

*Última atualização: Setembro 2025*
*Versão: 1.0*
*Equipe: EmployeeVirtual Development Team*
