"""
Factory principal para usuários
Delega para domain/users/user_factory.py
Seguindo padrão IT Valley Architecture
"""
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
        """
        Cria novo usuário
        
        Args:
            dto: Dados para criação
            
        Returns:
            UserEntity: Usuário criado
        """
        return DomainUserFactory.create_user(dto)
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica senha
        
        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
            
        Returns:
            bool: True se senha correta
        """
        return DomainUserFactory.verify_password(password, password_hash)
    
    @staticmethod
    def email_from(dto: UserCreateRequest) -> str:
        """
        Extrai email de DTO
        
        Args:
            dto: Dados de criação
            
        Returns:
            str: Email extraído
        """
        return DomainUserFactory.email_from(dto)
    
    @staticmethod
    def create_from_existing(user: UserEntity, updates: UserUpdateRequest) -> UserEntity:
        """
        Cria usuário atualizado
        
        Args:
            user: Usuário existente
            updates: Atualizações
            
        Returns:
            UserEntity: Usuário atualizado
        """
        return DomainUserFactory.create_from_existing(user, updates)
