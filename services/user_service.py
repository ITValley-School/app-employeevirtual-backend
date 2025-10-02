"""
Serviço de usuários - Implementação IT Valley
Orquestra casos de uso sem implementar regras de negócio
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from data.user_repository import UserRepository
from schemas.users.requests import UserCreateRequest, UserUpdateRequest, UserLoginRequest
from schemas.users.responses import UserResponse, UserDetailResponse, UserListResponse
from domain.users.user_entity import UserEntity
from factories.user_factory import UserFactory
from mappers.user_mapper import UserMapper


class UserService:
    """
    Serviço de usuários - Orquestrador
    Coordena fluxos sem implementar regras de negócio
    """
    
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
    
    def create_user(self, dto: UserCreateRequest) -> UserEntity:
        """
        Cria novo usuário
        
        Args:
            dto: Dados para criação
            
        Returns:
            UserEntity: Usuário criado
            
        Raises:
            ValueError: Se email já existe
        """
        # 1. Validações que dependem do repositório
        email = UserFactory.email_from(dto)
        if self.user_repository.exists_email(email):
            raise ValueError("Email já está em uso")
        
        # 2. Cria entidade via Factory
        user = UserFactory.create_user(dto)
        
        # 3. Persiste
        self.user_repository.add(user)
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[UserEntity]:
        """
        Busca usuário por ID
        
        Args:
            user_id: ID do usuário
            
        Returns:
            UserEntity: Usuário encontrado ou None
        """
        return self.user_repository.get_user_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Busca usuário por email
        
        Args:
            email: Email do usuário
            
        Returns:
            UserEntity: Usuário encontrado ou None
        """
        return self.user_repository.get_user_by_email(email)
    
    def update_user(self, user_id: str, dto: UserUpdateRequest) -> Optional[UserEntity]:
        """
        Atualiza usuário
        
        Args:
            user_id: ID do usuário
            dto: Dados para atualização
            
        Returns:
            UserEntity: Usuário atualizado ou None
        """
        # 1. Busca usuário
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        
        # 2. Validações que dependem do repositório
        if dto.email and dto.email != user.email:
            if self.user_repository.exists_email(dto.email):
                raise ValueError("Email já está em uso")
        
        # 3. Cria usuário atualizado via Factory
        updated_user = UserFactory.create_from_existing(user, dto)
        
        # 4. Persiste
        self.user_repository.update(updated_user)
        
        return updated_user
    
    def authenticate_user(self, dto: UserLoginRequest) -> dict:
        """
        Autentica usuário e gera token
        
        Args:
            dto: Dados de login
            
        Returns:
            dict: Resultado do login com user, token e dados
        """
        # 1. Busca usuário
        user = self.user_repository.get_user_by_email(dto.email)
        if not user:
            raise ValueError("Credenciais inválidas")
        
        # 2. Verifica senha via Factory
        if not UserFactory.verify_password(dto.password, user.password_hash):
            raise ValueError("Credenciais inválidas")
        
        # 3. Atualiza último login
        user.update_last_login()
        self.user_repository.update(user)
        
        # 4. Gera token
        from auth.jwt_service import JWTService
        from config.settings import settings
        
        jwt_service = JWTService()
        access_token = jwt_service.create_access_token(
            data={"sub": user.get_id(), "email": user.get_email()}
        )
        
        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    
    def list_users(self, page: int = 1, size: int = 10, status: Optional[str] = None) -> tuple[List[UserEntity], int]:
        """
        Lista usuários
        
        Args:
            page: Página
            size: Tamanho da página
            status: Filtro por status
            
        Returns:
            tuple: (usuários, total)
        """
        return self.user_repository.list_users(page, size, status)
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca estatísticas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            dict: Estatísticas ou None
        """
        return self.user_repository.get_user_stats(user_id)
    
    def change_user_plan(self, user_id: str, new_plan: str) -> Optional[UserEntity]:
        """
        Altera plano do usuário
        
        Args:
            user_id: ID do usuário
            new_plan: Novo plano
            
        Returns:
            UserEntity: Usuário atualizado ou None
        """
        # 1. Busca usuário
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        
        # 2. Altera plano (regra de negócio na entidade)
        user.change_plan(new_plan)
        
        # 3. Persiste
        self.user_repository.update(user)
        
        return user
    
    def activate_user(self, user_id: str) -> Optional[UserEntity]:
        """
        Ativa usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            UserEntity: Usuário ativado ou None
        """
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        
        user.activate()
        self.user_repository.update(user)
        
        return user
    
    def deactivate_user(self, user_id: str) -> Optional[UserEntity]:
        """
        Desativa usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            UserEntity: Usuário desativado ou None
        """
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        
        user.deactivate()
        self.user_repository.update(user)
        
        return user
