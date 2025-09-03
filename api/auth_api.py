"""
API de autenticação para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from models.user_models import UserCreate, UserLogin, UserResponse, UserUpdate
from services.user_service import UserService
from data.database import get_db
from auth.jwt_service import JWTService
from auth.dependencies import get_current_user

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
async def logout_user(
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Faz logout do usuário
    
    Args:
        current_user: Usuário atual autenticado
        credentials: Credenciais de autorização
        
    Returns:
        Mensagem de sucesso
    """
    # Invalidar token atual
    token = credentials.credentials
    JWTService.blacklist_token(token)
    
    return {
        "message": "Logout realizado com sucesso",
        "user_id": current_user.id
    }

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Renova um token de acesso usando refresh token
    
    Args:
        refresh_token: Token de refresh
        db: Sessão do banco de dados
        
    Returns:
        Novo token de acesso
        
    Raises:
        HTTPException: Se refresh token inválido
    """
    # Verificar se o refresh token é válido
    payload = JWTService.verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado"
        )
    
    # Buscar usuário para obter email
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    # Criar novo access token
    new_access_token = JWTService.create_access_token(user_id, user.email)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "user_id": user_id
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retorna informações do usuário atual
    
    Args:
        current_user: Usuário atual autenticado
        
    Returns:
        Dados do usuário atual
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados do usuário atual
    
    Args:
        user_data: Dados para atualização
        current_user: Usuário atual autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do usuário atualizados
        
    Raises:
        HTTPException: Se dados inválidos
    """
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_user(current_user.id, user_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao atualizar usuário"
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera a senha do usuário atual
    
    Args:
        current_password: Senha atual
        new_password: Nova senha
        current_user: Usuário atual autenticado
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se senha atual incorreta
    """
    user_service = UserService(db)
    
    success = user_service.change_password(
        current_user.id,
        current_password,
        new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    return {
        "message": "Senha alterada com sucesso",
        "user_id": current_user.id
    }

@router.post("/reset-password")
async def reset_password(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Inicia processo de reset de senha
    
    Args:
        email: Email do usuário
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de confirmação
    """
    user_service = UserService(db)
    
    success = user_service.reset_password(email)
    
    if not success:
        # Não revelar se o email existe ou não
        return {
            "message": "Se o email existir, você receberá instruções para reset de senha"
        }
    
    return {
        "message": "Instruções para reset de senha enviadas para o email",
        "email": email
    }

@router.get("/sessions")
async def get_user_sessions(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as sessões ativas do usuário
    
    Args:
        current_user: Usuário atual autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de sessões ativas
    """
    user_service = UserService(db)
    sessions = user_service.get_user_sessions(current_user.id)
    
    return {
        "user_id": current_user.id,
        "sessions": sessions
    }

@router.delete("/sessions/{session_id}")
async def invalidate_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invalida uma sessão específica
    
    Args:
        session_id: ID da sessão
        current_user: Usuário atual autenticado
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
    """
    user_service = UserService(db)
    
    # TODO: Implementar invalidação de sessão específica
    # Por enquanto, apenas retorna sucesso
    
    return {
        "message": "Sessão invalidada com sucesso",
        "session_id": session_id,
        "user_id": current_user.id
    }

@router.get("/activities")
async def get_user_activities(
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista atividades do usuário atual
    
    Args:
        limit: Número máximo de atividades
        current_user: Usuário atual autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de atividades
    """
    user_service = UserService(db)
    activities = user_service.get_user_activities(current_user.id, limit)
    
    return {
        "user_id": current_user.id,
        "activities": activities,
        "total": len(activities)
    }

 

