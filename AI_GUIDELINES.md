# 🤖 AI Development Guidelines - EmployeeVirtual

## 🎯 Instruções para IA/Copilot

Este documento contém instruções específicas para assistentes de IA que trabalham no projeto EmployeeVirtual.

---

## 📋 Contexto do Projeto

### Arquitetura Atual
- **Clean Architecture** com separação de camadas
- **Domain-Driven Design (DDD)** 
- **Dependency Injection** via FastAPI
- **Repository Pattern** para acesso a dados
- **Service Layer** para lógica de negócio

### Estrutura de Pastas
```
employeevirtual/
├── api/                    # Controllers HTTP
├── services/               # Business Logic
├── data/                   # Repositories  
├── models/                 # DTOs e Entities
├── dependencies/           # Service Providers
├── auth/                   # Authentication
└── middlewares/            # Interceptors
```

---

## 🎭 Princípios Obrigatórios

### 1. **Single Responsibility Principle**
- Cada classe deve ter UMA única responsabilidade
- Controllers: apenas HTTP handling
- Services: apenas business logic
- Repositories: apenas data access

### 2. **Dependency Injection**
- SEMPRE use service providers
- NUNCA instancie services manualmente nos controllers
- NUNCA use `db: Session = Depends(get_db)` nos controllers

### 3. **Layer Separation**
- Controllers NÃO devem acessar repositories diretamente
- Services NÃO devem lidar com HTTP
- Repositories NÃO devem conter business logic

---

## 🔧 Padrões de Implementação

### ✅ Controller Pattern (CORRETO)
```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)  # ✅ Service injection
):
    """Controller responsabilidade: HTTP only"""
    try:
        return user_service.create_user(user_data, current_user.id)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### ❌ Anti-Pattern (INCORRETO)
```python
@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)  # ❌ Direct DB access
):
    # ❌ Business logic in controller
    if user_exists(user_data.email):
        raise HTTPException(400, "User exists")
    
    # ❌ Direct DB access
    user = UserEntity(**user_data.dict())
    db.add(user)
    db.commit()
```

### ✅ Service Pattern (CORRETO)
```python
class UserService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)  # ✅ Repository injection
    
    def create_user(self, user_data: UserCreate, created_by: int) -> UserResponse:
        # ✅ Business validation
        if self.user_repository.email_exists(user_data.email):
            raise BusinessException("Email já existe")
        
        # ✅ Use repository
        user = self.user_repository.create(user_data)
        return UserResponse.from_entity(user)
```

### ✅ Repository Pattern (CORRETO)
```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_data: UserCreate) -> UserEntity:
        # ✅ Only data access
        user = UserEntity(**user_data.dict())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
```

---

## 🤖 Prompts para IA

### Para Implementar Nova Funcionalidade
```
Crie uma funcionalidade completa de [FUNCIONALIDADE] seguindo a arquitetura clean 
do projeto EmployeeVirtual:

1. Models com DTOs de request/response
2. Repository apenas para acesso a dados
3. Service com lógica de negócio
4. Service provider para injeção de dependência
5. Controller usando service injection
6. Seguir padrões do ARCHITECTURE_GUIDE.md

Não use db: Session nos controllers, use service injection.
```

### Para Refatorar Código Existente
```
Refatore este código para seguir a arquitetura clean do EmployeeVirtual:

1. Separar responsabilidades por camada
2. Implementar dependency injection
3. Remover lógica de negócio dos controllers
4. Usar repository pattern para dados
5. Seguir princípio de responsabilidade única

Código atual: [CÓDIGO]
```

### Para Code Review
```
Revise este código seguindo as diretrizes do ARCHITECTURE_GUIDE.md:

1. Cada classe tem uma única responsabilidade?
2. Dependencies estão sendo injetadas corretamente?
3. Camadas estão bem separadas?
4. Há vazamento de responsabilidades?
5. Segue os padrões do projeto?

Código: [CÓDIGO]
```

---

## ⚡ Comandos Rápidos para IA

### Criar Nova Funcionalidade
```
"Implemente um CRUD completo para [ENTIDADE] seguindo os templates 
do IMPLEMENTATION_TEMPLATES.md e a arquitetura do ARCHITECTURE_GUIDE.md"
```

### Adicionar Endpoint
```
"Crie um endpoint [MÉTODO] /[ROTA] que [FUNCIONALIDADE], usando service 
injection e seguindo os padrões de controller do projeto"
```

### Criar Service
```
"Crie um [NOME]Service para [FUNCIONALIDADE] com lógica de negócio, 
usando repository pattern e retornando DTOs adequados"
```

### Criar Repository
```
"Crie um [NOME]Repository para acesso aos dados de [ENTIDADE], 
apenas com operações de banco de dados, sem lógica de negócio"
```

---

## 🚨 Validações Obrigatórias

### Antes de Gerar Código
Sempre verifique:

1. **Service Provider existe?**
   - Se não existe, criar em `dependencies/service_providers.py`

2. **Models estão definidos?**
   - DTOs de request/response
   - Enums necessários
   - Validações Pydantic

3. **Repository segue padrão?**
   - Apenas acesso a dados
   - Sem lógica de negócio
   - Recebe Session no construtor

4. **Service segue padrão?**
   - Lógica de negócio apenas
   - Usa repositories para dados
   - Retorna DTOs

5. **Controller segue padrão?**
   - Service injection
   - Sem db: Session
   - Apenas HTTP handling

### Checklist de Validação
```python
# ✅ Verificar se segue o padrão
def validate_architecture(code):
    checks = [
        "Usa service injection em controllers?",
        "Service tem apenas business logic?", 
        "Repository tem apenas data access?",
        "DTOs estão bem definidos?",
        "Service provider foi criado?",
        "Segue Single Responsibility Principle?"
    ]
    return all(checks)
```

---

## 📚 Referências Rápidas

### Imports Comuns
```python
# Controllers
from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.service_providers import get_[service_name]
from auth.dependencies import get_current_user

# Services  
from sqlalchemy.orm import Session
from data.[entity]_repository import [Entity]Repository

# Repositories
from sqlalchemy.orm import Session
from models.entities import [Entity]Entity

# Models
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
```

### Estrutura Base
```python
# Controller
@router.post("/endpoint", response_model=ResponseDTO)
async def action(
    data: RequestDTO,
    current_user: User = Depends(get_current_user),
    service: ServiceType = Depends(get_service)
):
    return service.method(data, current_user.id)

# Service
class Service:
    def __init__(self, db: Session):
        self.repository = Repository(db)
    
    def method(self, data: RequestDTO, user_id: int) -> ResponseDTO:
        # Business logic
        result = self.repository.operation(data)
        return ResponseDTO.from_entity(result)

# Repository  
class Repository:
    def __init__(self, db: Session):
        self.db = db
    
    def operation(self, data: RequestDTO) -> Entity:
        # Data access only
        pass
```

---

## 🎯 Objetivos da IA

### Sempre Busque
1. **Consistência** - Seguir padrões estabelecidos
2. **Separação de Responsabilidades** - Cada camada com sua função
3. **Baixo Acoplamento** - Usar dependency injection
4. **Alta Coesão** - Funcionalidades relacionadas juntas
5. **Legibilidade** - Código fácil de entender

### Sempre Evite
1. **God Classes** - Classes que fazem tudo
2. **Tight Coupling** - Dependências diretas
3. **Mixed Responsibilities** - Lógica em camada errada
4. **Code Duplication** - Repetição desnecessária
5. **Magic Numbers/Strings** - Usar constantes/enums

---

## ✅ Fluxo de Validação

### Antes de Implementar
1. [ ] Entendi a funcionalidade solicitada?
2. [ ] Identifiquei qual camada será afetada?
3. [ ] Service provider existe ou precisa ser criado?
4. [ ] Models necessários estão definidos?

### Durante a Implementação
1. [ ] Estou seguindo o padrão da camada?
2. [ ] Responsabilidades estão separadas?
3. [ ] Usando dependency injection?
4. [ ] DTOs estão corretos?

### Após Implementar
1. [ ] Código segue ARCHITECTURE_GUIDE.md?
2. [ ] Não há vazamento de responsabilidades?
3. [ ] Service provider foi atualizado se necessário?
4. [ ] Imports estão corretos?

---

## 🎮 Comandos de Debug

### Testar Service Providers
```python
# Validar se todos os providers funcionam
from dependencies.service_providers import *
print("✅ Todos os service providers OK!")
```

### Validar Imports
```python
# Testar imports específicos
from services.[service_name] import [ServiceClass]
from data.[repo_name] import [RepoClass]
print("✅ Imports funcionando!")
```

---

## 🚀 Resultado Esperado

Após seguir estas diretrizes, o código deve ser:

- **Limpo** - Fácil de ler e entender
- **Testável** - Dependencies podem ser mockadas
- **Manutenível** - Mudanças são isoladas por camada
- **Escalável** - Novas funcionalidades seguem o padrão
- **Consistente** - Todo o time segue a mesma arquitetura

---

*Use este guia como referência constante ao trabalhar no projeto EmployeeVirtual!* 🎯

---

*Última atualização: Setembro 2025*
*Versão: 1.0* 
*Para: GitHub Copilot, ChatGPT, Claude e outros assistentes de IA*
