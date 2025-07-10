"""
API de autenticação para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from models.user_models import UserCreate, UserLogin, UserResponse, UserUpdate
from services.user_service_new import UserService
from data.database import get_db

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário
    
    Args:
        user_data: Dados do usuário
        db: Sessão do banco de dados
        
    Returns:
        Dados do usuário criado
        
    Raises:
        HTTPException: Se email já existe
    """
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(user_data)
        print(f"Usuário criado: {user.id} - {user.email}")
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica um usuário
    
    Args:
        login_data: Dados de login
        db: Sessão do banco de dados
        
    Returns:
        Token de acesso e dados do usuário
        
    Raises:
        HTTPException: Se credenciais inválidas
    """
    user_service = UserService(db)
    
    try:
        result = user_service.authenticate_user(login_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        return {
            "access_token": result["token"],
            "token_type": "bearer",
            "expires_at": result["expires_at"],
            "user": result["user"]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Faz logout do usuário
    
    Args:
        credentials: Credenciais de autorização
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
    """
    user_service = UserService(db)
    
    success = user_service.logout_user(credentials.credentials)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )
    
    return {"message": "Logout realizado com sucesso"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Busca dados do usuário atual
    
    Args:
        credentials: Credenciais de autorização
        db: Sessão do banco de dados
        
    Returns:
        Dados do usuário atual
        
    Raises:
        HTTPException: Se token inválido
    """
    user_service = UserService(db)
    
    user = user_service.get_user_by_token(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    return user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados do usuário atual
    
    Args:
        user_data: Dados a serem atualizados
        credentials: Credenciais de autorização
        db: Sessão do banco de dados
        
    Returns:
        Dados do usuário atualizado
        
    Raises:
        HTTPException: Se token inválido
    """
    user_service = UserService(db)
    
    # Verificar usuário atual
    current_user = user_service.get_user_by_token(credentials.credentials)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    # Atualizar usuário
    updated_user = user_service.update_user(current_user.id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return updated_user

@router.get("/activities")
async def get_user_activities(
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Busca atividades do usuário atual
    
    Args:
        limit: Limite de atividades
        credentials: Credenciais de autorização
        db: Sessão do banco de dados
        
    Returns:
        Lista de atividades
        
    Raises:
        HTTPException: Se token inválido
    """
    user_service = UserService(db)
    
    # Verificar usuário atual
    current_user = user_service.get_user_by_token(credentials.credentials)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    activities = user_service.get_user_activities(current_user.id, limit)
    
    return {
        "activities": activities,
        "total": len(activities)
    }


@router.get("/stats")
async def get_user_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Busca estatísticas do usuário atual
    
    Args:
        credentials: Credenciais de autorização
        db: Sessão do banco de dados
        
    Returns:
        Estatísticas do usuário
        
    Raises:
        HTTPException: Se token inválido
    """
    user_service = UserService(db)
    
    # Verificar usuário atual
    current_user = user_service.get_user_by_token(credentials.credentials)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    stats = user_service.get_user_stats(current_user.id)
    
    return stats

# Função auxiliar para obter usuário atual
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Dependency para obter usuário atual
    
    Args:
        credentials: Credenciais de autorização
        db: Sessão do banco de dados
        
    Returns:
        Usuário atual
        
    Raises:
        HTTPException: Se token inválido
    """
    user_service = UserService(db)
    
    user = user_service.get_user_by_token(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    return user

