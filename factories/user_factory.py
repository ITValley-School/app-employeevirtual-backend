"""
Factory principal para usuários
Delega para domain/users/user_factory.py
Seguindo padrão IT Valley Architecture
"""
from typing import Optional
from domain.users.user_factory import UserFactory as DomainUserFactory
from schemas.users.requests import UserCreateRequest, UserUpdateRequest
from domain.users.user_entity import UserEntity


class UserFactory:
    """
    Factory principal para usuários
    Delega para factory do domínio
    """

    @staticmethod
    def create_user(dto: UserCreateRequest) -> UserEntity:
        """Cria novo usuário"""
        return DomainUserFactory.create_user(dto)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica senha"""
        return DomainUserFactory.verify_password(password, password_hash)

    @staticmethod
    def email_from(dto) -> str:
        """Extrai email de qualquer DTO"""
        if hasattr(dto, 'email'):
            return dto.email or ''
        if isinstance(dto, dict):
            return dto.get('email', '')
        return ''

    @staticmethod
    def create_from_existing(user: UserEntity, updates: UserUpdateRequest) -> UserEntity:
        """Cria usuário atualizado"""
        return DomainUserFactory.create_from_existing(user, updates)

    # ========== HELPERS PARA LOGIN/AUTH ==========

    @staticmethod
    def password_from(dto) -> str:
        """Extrai senha do DTO de login"""
        if hasattr(dto, 'password'):
            return dto.password or ''
        if isinstance(dto, dict):
            return dto.get('password', '')
        return ''

    @staticmethod
    def email_from_update(dto) -> Optional[str]:
        """Extrai email do DTO de atualização (pode ser None)"""
        if hasattr(dto, 'email'):
            return dto.email
        if isinstance(dto, dict):
            return dto.get('email')
        return None

    # ========== HELPERS PARA ENTITY ==========

    @staticmethod
    def id_from(user) -> str:
        """Extrai ID da entidade de usuário"""
        return getattr(user, 'id', '')

    @staticmethod
    def email_from_entity(user) -> str:
        """Extrai email da entidade de usuário"""
        return getattr(user, 'email', '')

    @staticmethod
    def password_hash_from(user) -> str:
        """Extrai password_hash da entidade de usuário"""
        return getattr(user, 'password_hash', '')

    @staticmethod
    def verify_credentials(dto, user) -> bool:
        """Verifica credenciais extraindo dados via Factory"""
        password = UserFactory.password_from(dto)
        password_hash = UserFactory.password_hash_from(user)
        return DomainUserFactory.verify_password(password, password_hash)

    @staticmethod
    def get_auth_info(user) -> dict:
        """Extrai informações de autenticação da entidade"""
        return {
            'id': getattr(user, 'id', ''),
            'email': getattr(user, 'email', ''),
        }

    @staticmethod
    def emails_match(dto_email: Optional[str], entity_email: str) -> bool:
        """Verifica se email do DTO é diferente do email da entidade"""
        if not dto_email:
            return True
        return dto_email == entity_email
