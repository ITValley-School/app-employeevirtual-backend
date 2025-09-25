"""
Serviço JWT - EmployeeVirtual
"""
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Set
import logging

from auth.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM, 
    JWT_ISSUER,
    JWT_TYPE_ACCESS,
    JWT_TYPE_REFRESH,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from models.uuid_models import validate_uuid

# Blacklist de tokens em memória
_token_blacklist: Set[str] = set()

class JWTService:
    
    @staticmethod
    def _get_token_hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """
        Cria um token de acesso
        
        Args:
            user_id: UUID do usuário
            email: Email do usuário
            
        Returns:
            Token JWT de acesso
        """
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
            
        return JWTService._create_token(
            user_id=user_id,
            email=email,
            token_type=JWT_TYPE_ACCESS,
            expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Cria um token de refresh
        
        Args:
            user_id: UUID do usuário
            
        Returns:
            Token JWT de refresh
        """
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
            
        return JWTService._create_token(
            user_id=user_id,
            email=None,
            token_type=JWT_TYPE_REFRESH,
            expires_days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    @staticmethod
    def _create_token(
        user_id: str, 
        email: Optional[str], 
        token_type: str,
        expires_minutes: Optional[int] = None,
        expires_days: Optional[int] = None
    ) -> str:
        """
        Cria um token JWT
        
        Args:
            user_id: UUID do usuário
            email: Email do usuário (opcional)
            token_type: Tipo do token
            expires_minutes: Expiração em minutos
            expires_days: Expiração em dias
            
        Returns:
            Token JWT codificado
        """
        if expires_days:
            expire = datetime.utcnow() + timedelta(days=expires_days)
        else:
            expire = datetime.utcnow() + timedelta(minutes=expires_minutes or 15)
        
        payload = {
            "sub": user_id,  # UUID como string
            "exp": expire,
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),
            "type": token_type,
            "iss": JWT_ISSUER,
        }
        
        if email and token_type == JWT_TYPE_ACCESS:
            payload["email"] = email
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM), payload["exp"]
    
    @staticmethod
    def verify_token(token: str, expected_type: str = JWT_TYPE_ACCESS) -> Dict[str, Any]:
        """
        Verifica e decodifica um token JWT
        
        Args:
            token: Token JWT a ser verificado
            expected_type: Tipo esperado do token
            
        Returns:
            Payload do token
            
        Raises:
            ExpiredSignatureError: Token expirado
            InvalidTokenError: Token inválido
        """
        try:
            token_hash = JWTService._get_token_hash(token)
            if token_hash in _token_blacklist:
                raise InvalidTokenError("Token foi invalidado")
            
            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
                options={
                    "require_exp": True,
                    "require_iat": True,
                    "require_nbf": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "verify_signature": True
                }
            )
            
            if payload.get("type") != expected_type:
                raise InvalidTokenError(f"Tipo de token incorreto: {payload.get('type')}")
            if payload.get("iss") != JWT_ISSUER:
                raise InvalidTokenError("Emissor do token inválido")
            
            # Verificar se o user_id é um UUID válido
            user_id = payload.get("sub")
            if not user_id or not validate_uuid(user_id):
                raise InvalidTokenError("User ID inválido no token")
            
            return payload
            
        except ExpiredSignatureError:
            logging.warning("Token expirado detectado")
            raise  # Re-raise para capturar no dependencies
        except InvalidTokenError:
            logging.warning("Token inválido detectado")
            raise  # Re-raise para capturar no dependencies
        except Exception as e:
            logging.error(f"Erro inesperado ao verificar token: {e}")
            raise InvalidTokenError(f"Erro ao verificar token: {str(e)}")
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """
        Extrai o user_id de um token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            UUID do usuário ou None se inválido
        """
        try:
            payload = JWTService.verify_token(token)
            user_id = payload.get("sub")
            if validate_uuid(user_id):
                return user_id
        except (ExpiredSignatureError, InvalidTokenError):
            pass
        return None
    
    @staticmethod
    def get_email_from_token(token: str) -> Optional[str]:
        """
        Extrai o email de um token JWT de acesso
        
        Args:
            token: Token JWT de acesso
            
        Returns:
            Email do usuário ou None se não disponível
        """
        try:
            payload = JWTService.verify_token(token, JWT_TYPE_ACCESS)
            return payload.get("email")
        except (ExpiredSignatureError, InvalidTokenError):
            return None
    
    @staticmethod
    def blacklist_token(token: str) -> bool:
        """
        Adiciona um token à blacklist
        
        Args:
            token: Token a ser invalidado
            
        Returns:
            True se adicionado com sucesso
        """
        try:
            token_hash = JWTService._get_token_hash(token)
            _token_blacklist.add(token_hash)
            return True
        except Exception:
            return False
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """
        Verifica se um token está na blacklist
        
        Args:
            token: Token a ser verificado
            
        Returns:
            True se está na blacklist
        """
        try:
            token_hash = JWTService._get_token_hash(token)
            return token_hash in _token_blacklist
        except Exception:
            return True
    
    @staticmethod
    def clear_blacklist() -> int:
        """
        Limpa a blacklist de tokens
        
        Returns:
            Número de tokens removidos
        """
        count = len(_token_blacklist)
        _token_blacklist.clear()
        return count
    
    @staticmethod
    def get_blacklist_size() -> int:
        """
        Retorna o tamanho atual da blacklist
        
        Returns:
            Número de tokens na blacklist
        """
        return len(_token_blacklist)
    
    @staticmethod
    def create_token_pair(user_id: str, email: str) -> Dict[str, str]:
        """
        Cria um par de tokens (access + refresh)
        
        Args:
            user_id: UUID do usuário
            email: Email do usuário
            
        Returns:
            Dicionário com access_token e refresh_token
        """
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
            
        access_token = JWTService.create_access_token(user_id, email)
        refresh_token = JWTService.create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """
        Cria um novo access_token usando um refresh_token válido
        
        Args:
            refresh_token: Token de refresh válido
            
        Returns:
            Novo access_token ou None se refresh_token inválido
        """
        try:
            payload = JWTService.verify_token(refresh_token, JWT_TYPE_REFRESH)
            
            user_id = payload.get("sub")
            if not user_id or not validate_uuid(user_id):
                return None
            
            # Criar novo access_token (sem email para refresh)
            return JWTService._create_token(
                user_id=user_id,
                email=None,
                token_type=JWT_TYPE_ACCESS,
                expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        except (ExpiredSignatureError, InvalidTokenError):
            return None