"""
API de usuários - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status, Query
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
from factories.user_factory import UserFactory
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
    """
    # Service orquestra criação e validações
    user = user_service.create_user(dto)
    
    # Converte para Response via Mapper
    return UserMapper.to_public(user)


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
    """
    # Service orquestra busca e validações
    result = user_service.get_user_detail(user_id)
    
    # Converte para Response
    return UserMapper.to_detail(result['user'], result['stats'])


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
    """
    # Service orquestra atualização e validações
    user = user_service.update_user(user_id, dto)
    
    # Converte para Response
    return UserMapper.to_public(user)


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
    # Service orquestra autenticação e geração de token
    login_result = user_service.authenticate_user(dto)
    
    # Converte para Response via Mapper
    return UserMapper.to_login_response(login_result)


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
    """
    # Service orquestra ativação e validações
    user = user_service.activate_user(user_id)
    
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
    """
    # Service orquestra desativação e validações
    user = user_service.deactivate_user(user_id)
    
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
    """
    # Service orquestra mudança de plano e validações
    user = user_service.change_user_plan(user_id, new_plan)
    
    return UserMapper.to_public(user)
