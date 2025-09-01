"""
Módulo de autenticação - EmployeeVirtual
"""

from .dependencies import (
    get_current_user,
    get_current_user_optional, 
    require_premium_user,
    require_admin_user,
)

from .jwt_service import JWTService, create_token_pair

from .config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    ERROR_MESSAGES
)

__all__ = [
    "get_current_user",
    "get_current_user_optional", 
    "require_premium_user",
    "require_admin_user",
    "JWTService",
    "create_token_pair",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "REFRESH_TOKEN_EXPIRE_DAYS",
    "ERROR_MESSAGES"
]