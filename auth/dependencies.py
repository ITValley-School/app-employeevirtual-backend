"""
Dependencies de autenticação - EmployeeVirtual
"""
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from models.user_models import UserResponse
from services.user_service import UserService
from data.database import get_db

from auth.jwt_service import JWTService
from auth.config import ERROR_MESSAGES

security = HTTPBearer(auto_error=False)

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
    db: Session = Depends(get_db)
) -> UserResponse:
    
    token = extract_token_from_request(request, credentials)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["TOKEN_NOT_PROVIDED"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = JWTService.verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["TOKEN_INVALID"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str or not user_id_str.isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["TOKEN_MALFORMED"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(user_id_str)
    
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
    db: Session = Depends(get_db)
) -> Optional[UserResponse]:
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException:
        return None

async def require_premium_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    premium_plans = ["premium", "enterprise", "admin"]
    
    if current_user.plan not in premium_plans:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=ERROR_MESSAGES["PREMIUM_REQUIRED"]
        )
    
    return current_user

async def require_admin_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        return current_user
    
    if current_user.plan == "admin":
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=ERROR_MESSAGES["ADMIN_REQUIRED"]
    )

async def verify_token_only(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    token = extract_token_from_request(request, credentials)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["TOKEN_NOT_PROVIDED"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = JWTService.verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["TOKEN_INVALID"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": int(payload.get("sub")),
        "email": payload.get("email"),
        "jti": payload.get("jti"),
        "issued_at": payload.get("iat"),
        "expires_at": payload.get("exp")
    }