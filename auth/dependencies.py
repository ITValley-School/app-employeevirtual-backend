"""
Dependencies de autenticação - EmployeeVirtual
"""
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from schemas.users.responses import UserResponse
from services.user_service import UserService
from config.database import db_config
from data.entities.user_entities import UserEntity

from auth.jwt_service import JWTService
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from auth.config import ERROR_MESSAGES
import logging
import re

security = HTTPBearer(auto_error=False)

def validate_uuid(uuid_string: str) -> bool:
    """Valida se uma string é um UUID válido"""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))

def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def extract_token_from_request(request: Request, credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[str]:
    if credentials and credentials.credentials:
        return credentials.credentials
    
    return request.cookies.get("access_token")

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(db_config.get_session)
) -> UserEntity:
    
    
    token = extract_token_from_request(request, credentials)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["TOKEN_NOT_PROVIDED"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = JWTService.verify_token(token, "access")
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seu token expirou. Por favor, faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido. Acesso negado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id or (len(user_id) != 32 and len(user_id) != 36):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["TOKEN_MALFORMED"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["USER_NOT_FOUND"],
        )
    
    return user

async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(db_config.get_session)
) -> Optional[UserResponse]:
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException:
        return None

async def require_premium_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    premium_plans = ["pro", "enterprise"]
    
    if current_user.plan not in premium_plans:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=ERROR_MESSAGES["PREMIUM_REQUIRED"]
        )
    
    return current_user

async def require_enterprise_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if current_user.plan != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=ERROR_MESSAGES["ENTERPRISE_REQUIRED"]
        )
    
    return current_user

async def require_admin_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if current_user.plan != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES["ADMIN_REQUIRED"]
        )
    
    return current_user

async def get_current_user_id(
    current_user: UserResponse = Depends(get_current_user)
) -> str:
    """Retorna apenas o ID do usuário atual"""
    return current_user.id

async def get_current_user_plan(
    current_user: UserResponse = Depends(get_current_user)
) -> str:
    """Retorna apenas o plano do usuário atual"""
    return current_user.plan

async def get_current_user_status(
    current_user: UserResponse = Depends(get_current_user)
) -> str:
    """Retorna apenas o status do usuário atual"""
    return current_user.status

async def require_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Verifica se o usuário está ativo"""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES["USER_INACTIVE"]
        )
    
    return current_user

async def require_verified_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Verifica se o usuário está verificado (pode ser expandido no futuro)"""
    # Por enquanto, apenas verifica se está ativo
    return await require_active_user(current_user)

async def get_user_context(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """Retorna contexto completo do usuário para logging e auditoria"""
    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "user_plan": current_user.plan,
        "user_status": current_user.status,
        "client_ip": get_client_ip(request),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "request_id": request.headers.get("x-request-id", "unknown")
    }