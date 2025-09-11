# 🛠️ Templates de Implementação - EmployeeVirtual

## 📋 Como Implementar Novos Recursos

Este documento fornece templates prontos para implementar novos recursos seguindo nossa arquitetura clean.

---

## 🎯 Template: Nova Funcionalidade Completa

### Exemplo: Sistema de Notificações

#### 1. 📄 Modelos (models/notification_models.py)
```python
"""
Modelos para sistema de notificações
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

# Enums
class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

# DTOs de Request
class NotificationCreate(BaseModel):
    """DTO para criação de notificação"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: NotificationType = NotificationType.INFO
    user_id: int = Field(..., gt=0)

class NotificationUpdate(BaseModel):
    """DTO para atualização de notificação"""
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None

# DTOs de Response
class NotificationResponse(BaseModel):
    """DTO para resposta de notificação"""
    id: int
    title: str
    message: str
    type: NotificationType
    status: NotificationStatus
    user_id: int
    created_at: datetime
    read_at: Optional[datetime]
    
    @classmethod
    def from_entity(cls, entity) -> "NotificationResponse":
        """Converte entidade para response DTO"""
        return cls(
            id=entity.id,
            title=entity.title,
            message=entity.message,
            type=entity.type,
            status=entity.status,
            user_id=entity.user_id,
            created_at=entity.created_at,
            read_at=entity.read_at
        )

class NotificationListResponse(BaseModel):
    """Response para lista de notificações"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
```

#### 2. 💾 Repository (data/notification_repository.py)
```python
"""
Repository para acesso aos dados de notificações
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from models.entities import NotificationEntity
from models.notification_models import NotificationCreate, NotificationUpdate, NotificationStatus

class NotificationRepository:
    """Repository para operações de notificações"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, notification_data: NotificationCreate) -> NotificationEntity:
        """Cria uma nova notificação"""
        notification = NotificationEntity(
            title=notification_data.title,
            message=notification_data.message,
            type=notification_data.type,
            user_id=notification_data.user_id,
            status=NotificationStatus.UNREAD
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def find_by_id(self, notification_id: int) -> Optional[NotificationEntity]:
        """Busca notificação por ID"""
        return self.db.query(NotificationEntity).filter(
            NotificationEntity.id == notification_id
        ).first()
    
    def find_by_user(self, user_id: int, status: Optional[NotificationStatus] = None) -> List[NotificationEntity]:
        """Busca notificações por usuário"""
        query = self.db.query(NotificationEntity).filter(
            NotificationEntity.user_id == user_id
        )
        
        if status:
            query = query.filter(NotificationEntity.status == status)
        
        return query.order_by(desc(NotificationEntity.created_at)).all()
    
    def count_unread_by_user(self, user_id: int) -> int:
        """Conta notificações não lidas do usuário"""
        return self.db.query(NotificationEntity).filter(
            and_(
                NotificationEntity.user_id == user_id,
                NotificationEntity.status == NotificationStatus.UNREAD
            )
        ).count()
    
    def update(self, notification_id: int, update_data: NotificationUpdate) -> Optional[NotificationEntity]:
        """Atualiza notificação"""
        notification = self.find_by_id(notification_id)
        if not notification:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(notification, field, value)
        
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def delete(self, notification_id: int) -> bool:
        """Remove notificação"""
        notification = self.find_by_id(notification_id)
        if not notification:
            return False
        
        self.db.delete(notification)
        self.db.commit()
        return True
```

#### 3. 🔧 Service (services/notification_service.py)
```python
"""
Serviço para lógica de negócio de notificações
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from data.notification_repository import NotificationRepository
from data.user_repository import UserRepository
from models.notification_models import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationListResponse, NotificationStatus
)

class NotificationService:
    """Serviço para gerenciamento de notificações"""
    
    def __init__(self, db: Session):
        self.notification_repository = NotificationRepository(db)
        self.user_repository = UserRepository(db)
    
    def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        """
        Cria uma nova notificação
        
        Regras de negócio:
        - Usuário deve existir
        - Validar permissões se necessário
        """
        # Validação: usuário existe
        user = self.user_repository.find_by_id(notification_data.user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        # Criar notificação
        notification = self.notification_repository.create(notification_data)
        
        # TODO: Implementar envio em tempo real (WebSocket, etc.)
        
        return NotificationResponse.from_entity(notification)
    
    def get_user_notifications(self, user_id: int, status: Optional[NotificationStatus] = None) -> NotificationListResponse:
        """
        Busca notificações do usuário
        
        Regras de negócio:
        - Apenas notificações do próprio usuário
        - Filtrar por status se especificado
        """
        # Buscar notificações
        notifications = self.notification_repository.find_by_user(user_id, status)
        unread_count = self.notification_repository.count_unread_by_user(user_id)
        
        # Converter para DTOs
        notification_responses = [
            NotificationResponse.from_entity(n) for n in notifications
        ]
        
        return NotificationListResponse(
            notifications=notification_responses,
            total=len(notification_responses),
            unread_count=unread_count
        )
    
    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[NotificationResponse]:
        """
        Marca notificação como lida
        
        Regras de negócio:
        - Apenas o dono pode marcar como lida
        - Atualizar timestamp de leitura
        """
        # Verificar se notificação pertence ao usuário
        notification = self.notification_repository.find_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return None
        
        # Marcar como lida
        update_data = NotificationUpdate(
            status=NotificationStatus.READ,
            read_at=datetime.now()
        )
        
        updated_notification = self.notification_repository.update(notification_id, update_data)
        
        return NotificationResponse.from_entity(updated_notification)
    
    def mark_all_as_read(self, user_id: int) -> int:
        """
        Marca todas as notificações do usuário como lidas
        
        Returns:
            Quantidade de notificações marcadas
        """
        unread_notifications = self.notification_repository.find_by_user(
            user_id, NotificationStatus.UNREAD
        )
        
        count = 0
        for notification in unread_notifications:
            update_data = NotificationUpdate(
                status=NotificationStatus.READ,
                read_at=datetime.now()
            )
            self.notification_repository.update(notification.id, update_data)
            count += 1
        
        return count
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """
        Remove notificação
        
        Regras de negócio:
        - Apenas o dono pode remover
        """
        notification = self.notification_repository.find_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return False
        
        return self.notification_repository.delete(notification_id)
```

#### 4. 🔌 Service Provider (dependencies/service_providers.py)
```python
# Adicionar ao arquivo existente

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """
    Provedor do NotificationService
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Instância do NotificationService
    """
    return NotificationService(db)
```

#### 5. 🌐 API Controller (api/notification_api.py)
```python
"""
API para gerenciamento de notificações
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List

from services.notification_service import NotificationService
from dependencies.service_providers import get_notification_service
from auth.dependencies import get_current_user
from models.notification_models import (
    NotificationCreate, NotificationResponse, NotificationListResponse,
    NotificationStatus
)
from models.user_models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Cria uma nova notificação
    
    Responsabilidades:
    - Validar dados de entrada
    - Chamar service
    - Retornar resposta HTTP
    """
    try:
        return notification_service.create_notification(notification_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    status: Optional[NotificationStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Lista notificações do usuário atual
    """
    return notification_service.get_user_notifications(current_user.id, status)

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Marca notificação como lida
    """
    result = notification_service.mark_as_read(notification_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return result

@router.patch("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Marca todas as notificações como lidas
    """
    count = notification_service.mark_all_as_read(current_user.id)
    return {"message": f"{count} notificações marcadas como lidas"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Remove notificação
    """
    success = notification_service.delete_notification(notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return {"message": "Notificação removida com sucesso"}
```

#### 6. 🔗 Registrar no Router Principal (main.py ou router_config.py)
```python
# Adicionar ao arquivo de configuração de routers
from api.notification_api import router as notification_router

app.include_router(notification_router, prefix="/api/v1")
```

---

## 🧪 Template: Testes

### Teste de Service
```python
# tests/services/test_notification_service.py
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from services.notification_service import NotificationService
from models.notification_models import NotificationCreate, NotificationStatus

class TestNotificationService:
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_db = Mock()
        self.notification_service = NotificationService(self.mock_db)
        
        # Mock repositories
        self.notification_service.notification_repository = Mock()
        self.notification_service.user_repository = Mock()
    
    def test_create_notification_success(self):
        """Teste: criar notificação com sucesso"""
        # Arrange
        notification_data = NotificationCreate(
            title="Test Notification",
            message="Test Message",
            user_id=1
        )
        
        # Mock user exists
        self.notification_service.user_repository.find_by_id.return_value = Mock(id=1)
        
        # Mock notification creation
        mock_notification = Mock()
        mock_notification.id = 1
        self.notification_service.notification_repository.create.return_value = mock_notification
        
        # Act
        result = self.notification_service.create_notification(notification_data)
        
        # Assert
        self.notification_service.user_repository.find_by_id.assert_called_once_with(1)
        self.notification_service.notification_repository.create.assert_called_once()
        assert result is not None
    
    def test_create_notification_user_not_found(self):
        """Teste: erro ao criar notificação - usuário não encontrado"""
        # Arrange
        notification_data = NotificationCreate(
            title="Test Notification",
            message="Test Message",
            user_id=999
        )
        
        # Mock user not found
        self.notification_service.user_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Usuário não encontrado"):
            self.notification_service.create_notification(notification_data)
```

---

## 🎯 Checklist Rápido

### ✅ Para cada nova funcionalidade:

1. **Models** 📄
   - [ ] DTOs de request definidos
   - [ ] DTOs de response definidos
   - [ ] Enums necessários
   - [ ] Validações Pydantic
   - [ ] Método `from_entity()` nos responses

2. **Repository** 💾
   - [ ] Herda padrões de CRUD
   - [ ] Queries específicas do domínio
   - [ ] Tratamento de exceções
   - [ ] Apenas acesso a dados

3. **Service** 🔧
   - [ ] Lógica de negócio implementada
   - [ ] Validações de domínio
   - [ ] Usa repositories para dados
   - [ ] Transações gerenciadas
   - [ ] Tratamento de exceções de negócio

4. **Service Provider** 🔌
   - [ ] Função get_*_service() criada
   - [ ] Dependências injetadas
   - [ ] Documentação presente

5. **API Controller** 🌐
   - [ ] Apenas lógica HTTP
   - [ ] Service injetado via Depends
   - [ ] Tratamento de exceções HTTP
   - [ ] Documentação OpenAPI
   - [ ] Response models corretos

6. **Testes** 🧪
   - [ ] Testes unitários do service
   - [ ] Mocks das dependências
   - [ ] Casos de sucesso e erro
   - [ ] Cobertura adequada

---

## 🚀 Comandos Úteis

### Gerar boilerplate
```bash
# Criar estrutura básica para nova funcionalidade
mkdir -p tests/services
touch models/{feature}_models.py
touch data/{feature}_repository.py
touch services/{feature}_service.py
touch api/{feature}_api.py
touch tests/services/test_{feature}_service.py
```

### Validar arquitetura
```python
# Validar se service providers estão funcionando
from dependencies.service_providers import *
print("Todos os service providers carregados com sucesso!")
```

---

*Use este template como base para implementar qualquer nova funcionalidade!* 🎯
