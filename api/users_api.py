"""
API de usuários - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.orm import Session

from schemas.users.requests import UserCreateRequest, UserUpdateRequest, UserLoginRequest
from schemas.users.responses import (
    UserResponse, 
    UserDetailResponse, 
    UserListResponse,
    UserLoginResponse
)
from services.user_service import UserService
from mappers.user_mapper import UserMapper
from config.database import db_config
from auth.dependencies import get_current_user
from auth.jwt_service import JWTService
from config.settings import settings

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: Session = Depends(db_config.get_session)) -> UserService:
    """Dependency para UserService"""
    return UserService(db)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    dto: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Cria novo usuário
    
    Args:
        dto: Dados do usuário
        user_service: Serviço de usuários
        
    Returns:
        UserResponse: Usuário criado
        
    Raises:
        HTTPException: Se email já existe
    """
    try:
        # 1. Cria usuário via Service
        user = user_service.create_user(dto)
        
        # 2. Converte para Response via Mapper
        return UserMapper.to_public(user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """
    Busca usuário por ID
    
    Args:
        user_id: ID do usuário
        user_service: Serviço de usuários
        current_user: Usuário autenticado
        
    Returns:
        UserDetailResponse: Dados detalhados do usuário
        
    Raises:
        HTTPException: Se usuário não encontrado
    """
    # Busca usuário
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Busca estatísticas
    stats = user_service.get_user_stats(user_id)
    
    # Converte para Response
    return UserMapper.to_detail(user, stats)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    dto: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """
    Atualiza usuário
    
    Args:
        user_id: ID do usuário
        dto: Dados para atualização
        user_service: Serviço de usuários
        current_user: Usuário autenticado
        
    Returns:
        UserResponse: Usuário atualizado
        
    Raises:
        HTTPException: Se usuário não encontrado ou email já existe
    """
    try:
        # Atualiza usuário
        user = user_service.update_user(user_id, dto)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Converte para Response
        return UserMapper.to_public(user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """
    Lista usuários
    
    Args:
        page: Página
        size: Tamanho da página
        status: Filtro por status
        user_service: Serviço de usuários
        current_user: Usuário autenticado
        
    Returns:
        UserListResponse: Lista de usuários
    """
    # Lista usuários
    users, total = user_service.list_users(page, size, status)
    
    # Converte para Response
    return UserMapper.to_list(users, total, page, size)


@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    dto: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Autentica usuário
    
    Args:
        dto: Dados de login
        user_service: Serviço de usuários
        
    Returns:
        UserLoginResponse: Dados de login
        
    Raises:
        HTTPException: Se credenciais inválidas
    """
    # Autentica usuário
    user = user_service.authenticate_user(dto)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Gera token
    jwt_service = JWTService()
    access_token = jwt_service.create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    # Converte usuário para Response
    user_response = UserMapper.to_public(user)
    
    return UserLoginResponse(
        user=user_response,
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """
    Ativa usuário
    
    Args:
        user_id: ID do usuário
        user_service: Serviço de usuários
        current_user: Usuário autenticado
        
    Returns:
        UserResponse: Usuário ativado
        
    Raises:
        HTTPException: Se usuário não encontrado
    """
    user = user_service.activate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UserMapper.to_public(user)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """
    Desativa usuário
    
    Args:
        user_id: ID do usuário
        user_service: Serviço de usuários
        current_user: Usuário autenticado
        
    Returns:
        UserResponse: Usuário desativado
        
    Raises:
        HTTPException: Se usuário não encontrado
    """
    user = user_service.deactivate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UserMapper.to_public(user)


@router.patch("/{user_id}/plan", response_model=UserResponse)
async def change_user_plan(
    user_id: str,
    new_plan: str,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """
    Altera plano do usuário
    
    Args:
        user_id: ID do usuário
        new_plan: Novo plano
        user_service: Serviço de usuários
        current_user: Usuário autenticado
        
    Returns:
        UserResponse: Usuário com plano alterado
        
    Raises:
        HTTPException: Se usuário não encontrado ou plano inválido
    """
    try:
        user = user_service.change_user_plan(user_id, new_plan)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return UserMapper.to_public(user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
