"""
API de autenticação para o sistema EmployeeVirtual
Usando ITValley Security SDK
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Dict, Any
import logging

# ITValley Security SDK - FastAPI Integration
from itvalleysecurity.fastapi import login_response, require_access

from models.user_models import UserCreate, UserLogin, UserResponse, UserUpdate
from services.user_service import UserService
from dependencies.service_providers import get_user_service

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Registra um novo usuário
    """
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login_user(
    login_data: UserLogin,
    response: Response,
    user_service: UserService = Depends(get_user_service)
):
    """
    Autentica um usuário usando ITValley Security SDK
    """
    try:
        # Autenticar usuário com o serviço existente
        result = user_service.authenticate_user(login_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        user = result["user"]
        
        # Verificar se usuário está ativo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        # Usar ITValley Security SDK para emitir tokens
        return login_response(
            response,
            sub=str(user.id),  # UUID como string
            email=user.email,
            set_cookies=True   # Configura cookies HttpOnly automaticamente
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no processo de login"
        )

@router.post("/logout")
async def logout_user(response: Response):
    """
    Logout simples - remove cookies do cliente
    """
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    
    return {"message": "Logout realizado com sucesso"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_token = Depends(require_access),
    user_service: UserService = Depends(get_user_service)
):
    """
    Retorna informações do usuário atual
    """
    user_id = user_token["sub"]
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    user_token = Depends(require_access),
    user_service: UserService = Depends(get_user_service)
):
    """
    Atualiza dados do usuário atual
    """
    try:
        user_id = user_token["sub"]
        updated_user = user_service.update_user(user_id, user_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    user_token = Depends(require_access),
    user_service: UserService = Depends(get_user_service)
):
    """
    Altera a senha do usuário atual
    """
    try:
        user_id = user_token["sub"]
        user_service.change_password(user_id, current_password, new_password)
        
        return {"message": "Senha alterada com sucesso"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/activities")
async def get_user_activities(
    limit: int = 10,
    user_token = Depends(require_access),
    user_service: UserService = Depends(get_user_service)
):
    """
    Retorna atividades do usuário
    """
    user_id = user_token["sub"]
    activities = user_service.get_user_activities(user_id, limit)
    
    return {
        "user_id": user_id,
        "activities": activities,
        "total": len(activities)
    }