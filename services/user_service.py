"""
Serviço de usuários - Implementação IT Valley
Orquestra casos de uso sem implementar regras de negócio
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from data.user_repository import UserRepository
from schemas.users.requests import UserCreateRequest, UserUpdateRequest, UserLoginRequest
from data.entities.user_entities import UserEntity as UserEntityDB
from factories.user_factory import UserFactory


class UserService:
    """
    Serviço de usuários - Orquestrador
    Coordena fluxos sem implementar regras de negócio
    """

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def create_user(self, dto: UserCreateRequest) -> UserEntityDB:
        """
        Cria novo usuário.
        Service apenas orquestra: Factory cria, Repository persiste.
        """
        # 1. Validações que dependem do repositório (usa helper da Factory)
        email = UserFactory.email_from(dto)
        if self.user_repository.exists_email(email):
            raise ValueError("Email já está em uso")

        # 2. Factory cria domain entity (conhece os campos do DTO)
        domain_user = UserFactory.create_user(dto)

        # 3. Repository persiste convertendo internamente via _to_model()
        return self.user_repository.save(domain_user)

    def get_user_by_id(self, user_id: str) -> Optional[UserEntityDB]:
        """Busca usuário por ID"""
        return self.user_repository.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[UserEntityDB]:
        """Busca usuário por email"""
        return self.user_repository.get_user_by_email(email)

    def get_user_detail(self, user_id: str) -> Dict[str, Any]:
        """Busca usuário com detalhes e estatísticas"""
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        stats = self.user_repository.get_user_stats(user_id)
        return {'user': user, 'stats': stats}

    def update_user(self, user_id: str, dto: UserUpdateRequest) -> Optional[UserEntityDB]:
        """Atualiza usuário"""
        # 1. Busca usuário
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None

        # 2. Validações via Factory helpers (Service não acessa campos)
        new_email = UserFactory.email_from_update(dto)
        current_email = UserFactory.email_from_entity(user)
        if not UserFactory.emails_match(new_email, current_email):
            if self.user_repository.exists_email(new_email):
                raise ValueError("Email já está em uso")

        # 3. Factory cria usuário atualizado (conhece os campos)
        updated_user = UserFactory.create_from_existing(user, dto)

        # 4. Repository persiste objeto inteiro
        self.user_repository.update(updated_user)

        return updated_user

    def authenticate_user(self, dto: UserLoginRequest) -> dict:
        """Autentica usuário e gera token"""
        # 1. Busca usuário via Factory helper (extrai email do DTO)
        email = UserFactory.email_from(dto)
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError("Credenciais inválidas")

        # 2. Verifica senha via Factory (Factory extrai campos internamente)
        if not UserFactory.verify_credentials(dto, user):
            raise ValueError("Credenciais inválidas")

        # 3. Gera token via Factory helper (extrai auth info da entity)
        from auth.jwt_service import JWTService
        from config.settings import settings

        auth_info = UserFactory.get_auth_info(user)
        jwt_service = JWTService()
        access_token = jwt_service.create_access_token(
            user_id=auth_info['id'],
            email=auth_info['email']
        )

        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }

    def refresh_token(self, token: str) -> dict:
        """
        Renova token JWT.
        Encapsula lógica de refresh que antes estava na API.
        """
        from auth.jwt_service import JWTService
        from config.settings import settings

        jwt_service = JWTService()
        payload = jwt_service.verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Token inválido")

        # Busca usuário para retornar dados atualizados
        user = self.user_repository.get_user_by_id(user_id)

        # Gera novo token
        new_token = jwt_service.create_access_token(user_id, payload.get("email", ""))

        return {
            "user": UserFactory.get_auth_info(user) if user else {"id": user_id, "email": payload.get("email", "")},
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }

    def list_users(self, page: int = 1, size: int = 10, status: Optional[str] = None) -> tuple[list, int]:
        """Lista usuários"""
        return self.user_repository.list_users(page, size, status)

    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca estatísticas do usuário"""
        return self.user_repository.get_user_stats(user_id)

    def change_user_plan(self, user_id: str, new_plan: str) -> Optional[UserEntityDB]:
        """Altera plano do usuário"""
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        user.change_plan(new_plan)
        self.user_repository.update(user)
        return user

    def activate_user(self, user_id: str) -> Optional[UserEntityDB]:
        """Ativa usuário"""
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        user.activate()
        self.user_repository.update(user)
        return user

    def deactivate_user(self, user_id: str) -> Optional[UserEntityDB]:
        """Desativa usuário"""
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        user.deactivate()
        self.user_repository.update(user)
        return user
