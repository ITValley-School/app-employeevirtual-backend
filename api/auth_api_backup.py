"""
API de autenticação para o sistema EmployeeVirtual
Usando ITValley Security SDK
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Dict, Any
import logging

# ITValley Security SDK - FastAPI Integration
from itvalleysecurity.fastapi import login_response, require_access
from itvalleysecurity.fastapi.payloads import LoginPayloadWithPassword
from itvalleysecurity.exceptions import InvalidToken

from models.user_models import UserCreate, UserLogin, UserResponse, UserUpdate
from services.user_service import UserService
from dependencies.service_providers import get_user_service


router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
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
    
    
    try:
        user = user_service.create_user(user_data)
        print(f"Usuário criado: {user.id} - {user.email}")
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
    
    Args:
        login_data: Dados de login (email e password)
        response: Response object para configurar cookies
        user_service: Serviço de usuários
        
    Returns:
        Resposta com tokens JWT usando ITValley Security SDK
        
    Raises:
        HTTPException: Se credenciais inválidas
    """
    try:
        # 1) Autenticar usuário com o serviço existente
        result = user_service.authenticate_user(login_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        user = result["user"]
        
        # 2) Verificar se usuário está ativo (regras extras)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        # 3) Usar ITValley Security SDK para emitir tokens
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
    user_service: UserService = Depends(get_user_service)
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
    # Verificar refresh token usando ITValley Security SDK
    try:
        payload = verify_refresh(refresh_token)
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token malformado"
            )
        
        # Buscar usuário para validar se ainda existe
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        # Gerar novo par de tokens usando SDK
        token_pair = issue_pair(
            sub=str(user.id),
            email=user.email
            # SDK usa configurações padrão para expiração
        )
        
        return {
            "access_token": token_pair["access_token"],
            "refresh_token": token_pair["refresh_token"],
            "token_type": token_pair["token_type"],
            "access_expires_at": token_pair["access_expires_at"],
            "refresh_expires_at": token_pair["refresh_expires_at"],
            "user_id": user_id
        }
        
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )
    except Exception as e:
        logging.error(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao renovar token"
        )

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
    user_service: UserService = Depends(get_user_service)
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
    user_service: UserService = Depends(get_user_service)
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
    user_service: UserService = Depends(get_user_service)
):
    """
    Inicia processo de reset de senha
    
    Args:
        email: Email do usuário
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de confirmação
    """
    
    
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
    user_service: UserService = Depends(get_user_service)
):
    """
    Lista todas as sessões ativas do usuário
    
    Args:
        current_user: Usuário atual autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de sessões ativas
    """
    
    sessions = user_service.get_user_sessions(current_user.id)
    
    return {
        "user_id": current_user.id,
        "sessions": sessions
    }

@router.delete("/sessions/{session_id}")
async def invalidate_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
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
    user_service: UserService = Depends(get_user_service)
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
    
    activities = user_service.get_user_activities(current_user.id, limit)
    
    return {
        "user_id": current_user.id,
        "activities": activities,
        "total": len(activities)
    }


# ============================================================================
# DEPENDENCY FUNCTIONS USANDO ITValley Security SDK
# ============================================================================

async def get_current_user_sdk(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Dependency para obter usuário atual usando ITValley Security SDK
    
    Args:
        credentials: Credenciais de autorização HTTP Bearer
        user_service: Serviço de usuários
        
    Returns:
        Dados do usuário atual
        
    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    try:
        # Verificar token de acesso usando SDK
        payload = verify_access(credentials.credentials)
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token malformado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Buscar usuário no banco
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logging.error(f"Erro na validação de token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na validação de token"
        )



