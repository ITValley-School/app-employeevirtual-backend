"""
Factory para usuários
Única porta de entrada para criação de entidades
Seguindo padrão IT Valley Architecture
"""
import hashlib
import secrets
from typing import Any
from datetime import datetime
from uuid import uuid4

from domain.users.user_entity import UserEntity
from schemas.users.requests import UserCreateRequest


class UserFactory:
    """
    Factory para criação de usuários
    Centraliza validações e criação de entidades
    """
    
    @staticmethod
    def create_user(dto: Any) -> UserEntity:
        """
        Cria nova entidade de usuário
        
        Args:
            dto: Dados para criação (UserCreateRequest, dict, etc.)
            
        Returns:
            UserEntity: Entidade criada
            
        Raises:
            ValueError: Se dados inválidos
        """
        # Helper para extrair dados de forma segura
        def _get(data: Any, key: str, default=None):
            if hasattr(data, key):
                return getattr(data, key)
            elif isinstance(data, dict):
                return data.get(key, default)
            return default
        
        # Extrai dados
        name = _get(dto, "name")
        email = _get(dto, "email")
        password = _get(dto, "password")
        plan = _get(dto, "plan", "free")
        
        # Validações básicas
        if not name or len(name.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        if not email or "@" not in email:
            raise ValueError("Email inválido")
        
        if not password or len(password) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        
        # Valida plano
        valid_plans = ["free", "basic", "pro", "enterprise"]
        if plan not in valid_plans:
            raise ValueError(f"Plano inválido: {plan}")
        
        # Hash da senha
        password_hash = UserFactory._hash_password(password)
        
        # Cria entidade
        return UserEntity(
            id=uuid4().hex,
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=password_hash,
            plan=plan,
            status="active",
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Gera hash da senha
        
        Args:
            password: Senha em texto plano
            
        Returns:
            str: Hash da senha
        """
        # Gera salt único
        salt = secrets.token_hex(16)
        
        # Hash com salt
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterações
        )
        
        # Retorna salt + hash
        return f"{salt}:{password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica se senha está correta
        
        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
            
        Returns:
            bool: True se senha correta
        """
        try:
            # Separa salt e hash
            salt, stored_hash = password_hash.split(":", 1)
            
            # Gera hash da senha fornecida
            password_hash_generated = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            # Compara hashes
            return password_hash_generated.hex() == stored_hash
            
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def email_from(dto: Any) -> str:
        """
        Helper para extrair email de DTO
        
        Args:
            dto: Dados (UserCreateRequest, dict, etc.)
            
        Returns:
            str: Email extraído
        """
        if hasattr(dto, "email"):
            return dto.email
        elif isinstance(dto, dict):
            return dto.get("email", "")
        return ""
    
    @staticmethod
    def id_from(dto: Any) -> str:
        """
        Helper para extrair ID de DTO
        
        Args:
            dto: Dados (UserResponse, dict, etc.)
            
        Returns:
            str: ID extraído
        """
        if hasattr(dto, "id"):
            return dto.id
        elif isinstance(dto, dict):
            return dto.get("id", "")
        return ""
    
    @staticmethod
    def create_from_existing(user: UserEntity, updates: Any) -> UserEntity:
        """
        Cria nova entidade baseada em existente com atualizações
        
        Args:
            user: Usuário existente
            updates: Dados para atualização
            
        Returns:
            UserEntity: Nova entidade atualizada
        """
        # Cria cópia
        updated_user = UserEntity(
            id=user.id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            plan=user.plan,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        
        # Aplica atualizações
        updated_user.apply_update_from_any(updates)
        
        return updated_user
