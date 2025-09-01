"""
Serviço JWT - EmployeeVirtual
"""
import jwt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Set

from auth.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM, 
    JWT_ISSUER,
    JWT_TYPE_ACCESS,
    JWT_TYPE_REFRESH,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

# Blacklist de tokens em memória
_token_blacklist: Set[str] = set()

class JWTService:
    
    @staticmethod
    def _get_token_hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        return JWTService._create_token(
            user_id=user_id,
            email=email,
            token_type=JWT_TYPE_ACCESS,
            expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        return JWTService._create_token(
            user_id=user_id,
            email=None,
            token_type=JWT_TYPE_REFRESH,
            expires_days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    @staticmethod
    def _create_token(
        user_id: int, 
        email: Optional[str], 
        token_type: str,
        expires_minutes: Optional[int] = None,
        expires_days: Optional[int] = None
    ) -> str:
        if expires_days:
            expire = datetime.utcnow() + timedelta(days=expires_days)
        else:
            expire = datetime.utcnow() + timedelta(minutes=expires_minutes or 15)
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),
            "type": token_type,
            "iss": JWT_ISSUER,
        }
        
        if email and token_type == JWT_TYPE_ACCESS:
            payload["email"] = email
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, expected_type: str = JWT_TYPE_ACCESS) -> Optional[Dict[str, Any]]:
        try:
            token_hash = JWTService._get_token_hash(token)
            if token_hash in _token_blacklist:
                return None
            
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
                return None
            if payload.get("iss") != JWT_ISSUER:
                return None
            
            iat = datetime.fromtimestamp(payload.get("iat", 0))
            max_age = timedelta(hours=24)
            if datetime.utcnow() - iat > max_age:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def blacklist_token(token: str) -> None:
        token_hash = JWTService._get_token_hash(token)
        _token_blacklist.add(token_hash)
    
    @staticmethod
    def is_blacklisted(token: str) -> bool:
        token_hash = JWTService._get_token_hash(token)
        return token_hash in _token_blacklist
    
    @staticmethod
    def extract_user_id(token: str) -> Optional[int]:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
                options={"verify_exp": False}
            )
            
            user_id_str = payload.get("sub")
            if user_id_str and user_id_str.isdigit():
                return int(user_id_str)
            
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def get_token_info(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False
                }
            )
            
            exp = payload.get("exp", 0)
            is_expired = datetime.utcnow().timestamp() > exp
            is_blacklisted = JWTService.is_blacklisted(token)
            
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "type": payload.get("type"),
                "issued_at": datetime.fromtimestamp(payload.get("iat", 0)),
                "expires_at": datetime.fromtimestamp(exp),
                "is_expired": is_expired,
                "is_blacklisted": is_blacklisted,
                "is_valid": not (is_expired or is_blacklisted),
                "jti": payload.get("jti"),
                "issuer": payload.get("iss")
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "valid": False
            }

def create_token_pair(user_id: int, email: str) -> Dict[str, Any]:
    access_token = JWTService.create_access_token(user_id, email)
    refresh_token = JWTService.create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user_id,
            "email": email
        }
    }

def revoke_token_pair(access_token: str, refresh_token: str) -> None:
    if access_token:
        JWTService.blacklist_token(access_token)
    if refresh_token:
        JWTService.blacklist_token(refresh_token)