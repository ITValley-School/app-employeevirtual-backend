"""
API de Autenticação - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from schemas.users.requests import UserCreateRequest, UserLoginRequest
from schemas.users.responses import UserLoginResponse, UserResponse
from services.user_service import UserService
from mappers.user_mapper import UserMapper
from config.database import db_config
from auth.jwt_service import JWTService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(db: Session = Depends(db_config.get_session)) -> UserService:
    """Dependency para UserService"""
    return UserService(db)


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login(
    dto: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Autentica usuário e retorna JWT token
    
    Args:
        dto: Email e senha do usuário
        user_service: Serviço de usuários
        
    Returns:
        UserLoginResponse: Dados de login com token JWT
        
    Raises:
        HTTPException: Se credenciais inválidas
    """
    try:
        # Service orquestra autenticação e geração de token
        login_result = user_service.authenticate_user(dto)
        
        # Converte para Response via Mapper
        return UserMapper.to_login_response(login_result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credenciais inválidas: {str(e)}"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    dto: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Registra novo usuário
    
    Args:
        dto: Dados do usuário (email, senha, nome)
        user_service: Serviço de usuários
        
    Returns:
        UserResponse: Usuário criado
        
    Raises:
        HTTPException: Se e-mail já existe
    """
    try:
        # Service orquestra criação
        user = user_service.create_user(dto)
        
        # Converte para Response
        return UserMapper.to_public(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao registrar: {str(e)}"
        )


@router.post("/refresh-token", response_model=UserLoginResponse)
async def refresh_token(
    token: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Renova o token JWT
    
    Args:
        token: Token JWT atual
        user_service: Serviço de usuários
        
    Returns:
        UserLoginResponse: Novo token JWT
        
    Raises:
        HTTPException: Se token inválido
    """
    try:
        jwt_service = JWTService()
        payload = jwt_service.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Gera novo token
        new_token = jwt_service.create_access_token(user_id, payload.get("email", ""))
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": payload.get("email")
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    Faz logout do usuário (limpa token no frontend)
    
    Returns:
        dict: Mensagem de logout bem-sucedido
    """
    # Logout é feito no frontend limpando localStorage
    # Este endpoint apenas confirma o logout
    return {"message": "Logout realizado com sucesso"}

