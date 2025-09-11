"""
Serviço de usuários para o sistema EmployeeVirtual - Nova implementação
Usa apenas repository para acesso a dados
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from data.user_repository import UserRepository
from models.user_models import UserCreate, UserUpdate, UserResponse, UserLogin
from models.dashboard_models import UsageMetrics
from models.uuid_models import validate_uuid


class UserService:
    """Serviço para gerenciamento de usuários - Nova implementação"""
    
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Cria um novo usuário
        
        Args:
            user_data: Dados do usuário a ser criado
            
        Returns:
            UserResponse: Dados do usuário criado
            
        Raises:
            ValueError: Se email já existe
        """
        # Verificar se email já existe
        existing_user = self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email já está em uso")
        
        # Hash da senha
        password_hash = self._hash_password(user_data.password)
        
        # Criar usuário
        db_user = self.user_repository.create_user(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            plan=user_data.plan
        )
        
        # Log da atividade
        self.user_repository.create_activity(
            user_id=db_user.id,
            activity_type="user_created",
            description=f"Usuário {user_data.name} criado com sucesso"
        )
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            plan=db_user.plan,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """
        Autentica um usuário
        
        Args:
            login_data: Dados de login
            
        Returns:
            Dict com dados do usuário e token, ou None se credenciais inválidas
        """
        user = self.user_repository.get_user_by_email(login_data.email)
        if not user:
            return None
        
        # Verificar senha
        if not self._verify_password(login_data.password, user.password_hash):
            return None
        
        # Atualizar último login
        self.user_repository.update_user(user.id, last_login=datetime.utcnow())
        
        # Criar sessão (7 dias)
        token = self.create_session(user.id, expires_in_hours=24*7)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Log da atividade
        self.user_repository.create_activity(
            user_id=user.id,
            activity_type="user_login",
            description="Login realizado com sucesso"
        )
        
        user_response = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            plan=user.plan,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        
        return {
            "user": user_response,
            "token": token,
            "expires_at": expires_at
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Busca usuário por ID
        
        Args:
            user_id: UUID do usuário
            
        Returns:
            UserResponse ou None se não encontrado
        """
        if not validate_uuid(user_id):
            return None
            
        db_user = self.user_repository.get_user_by_id(user_id)
        if not db_user:
            return None
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            plan=db_user.plan,
            status=db_user.status,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Busca usuário por email
        
        Args:
            email: Email do usuário
            
        Returns:
            UserResponse ou None se não encontrado
        """
        db_user = self.user_repository.get_user_by_email(email)
        if not db_user:
            return None
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            plan=db_user.plan,
            status=db_user.status,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Atualiza dados do usuário
        
        Args:
            user_id: UUID do usuário
            user_data: Dados a serem atualizados
            
        Returns:
            UserResponse atualizado ou None se não encontrado
        """
        if not validate_uuid(user_id):
            return None
            
        # Preparar dados para atualização
        update_data = {}
        if user_data.name is not None:
            update_data["name"] = user_data.name
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if user_data.plan is not None:
            update_data["plan"] = user_data.plan
        if user_data.status is not None:
            update_data["status"] = user_data.status
        
        if not update_data:
            return self.get_user_by_id(user_id)
        
        # Atualizar usuário
        db_user = self.user_repository.update_user(user_id, **update_data)
        if not db_user:
            return None
        
        # Log da atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="user_updated",
            description="Dados do usuário atualizados"
        )
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            plan=db_user.plan,
            status=db_user.status,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )
    
    def delete_user(self, user_id: str) -> bool:
        """
        Remove um usuário
        
        Args:
            user_id: UUID do usuário
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        if not validate_uuid(user_id):
            return False
            
        # Log da atividade antes de remover
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="user_deleted",
            description="Usuário removido do sistema"
        )
        
        return self.user_repository.delete_user(user_id)
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Lista usuários com paginação
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            
        Returns:
            Lista de usuários
        """
        db_users = self.user_repository.list_users(skip, limit)
        
        return [
            UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                plan=user.plan,
                status=user.status,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            for user in db_users
        ]
    
    def search_users(self, search_term: str, limit: int = 20) -> List[UserResponse]:
        """
        Busca usuários por nome ou email
        
        Args:
            search_term: Termo de busca
            limit: Número máximo de resultados
            
        Returns:
            Lista de usuários encontrados
        """
        db_users = self.user_repository.search_users(search_term, limit)
        
        return [
            UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                plan=user.plan,
                status=user.status,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            for user in db_users
        ]
    
    def get_user_metrics(self, user_id: str) -> Optional[UsageMetrics]:
        """
        Busca métricas do usuário
        
        Args:
            user_id: UUID do usuário
            
        Returns:
            UserMetrics ou None se não encontrado
        """
        if not validate_uuid(user_id):
            return None
            
        stats = self.user_repository.get_user_stats(user_id)
        if not stats:
            return None
        
        return UsageMetrics(
            user_id=stats["user_id"],
            total_agents=stats.get("total_agents", 0),
            total_flows=stats.get("total_flows", 0),
            total_executions=stats.get("total_executions", 0),
            active_sessions=stats.get("active_sessions", 0),
            total_activities=stats.get("total_activities", 0),
            last_activity=stats.get("last_activity"),
            created_at=stats["created_at"],
            last_login=stats["last_login"]
        )
    
    def create_session(self, user_id: str, expires_in_hours: int = 24) -> str:
        """
        Cria uma nova sessão para o usuário
        
        Args:
            user_id: UUID do usuário
            expires_in_hours: Horas até expirar
            
        Returns:
            Token da sessão
        """
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
            
        # Gerar token único
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        # Criar sessão no banco
        self.user_repository.create_session(user_id, token, expires_at)
        
        return token
    
    def validate_session(self, token: str) -> Optional[str]:
        """
        Valida uma sessão e retorna o user_id
        
        Args:
            token: Token da sessão
            
        Returns:
            UUID do usuário ou None se sessão inválida
        """
        session = self.user_repository.get_session_by_token(token)
        if not session:
            return None
        
        return session.user_id
    
    def invalidate_session(self, token: str) -> bool:
        """
        Invalida uma sessão
        
        Args:
            token: Token da sessão
            
        Returns:
            True se invalidada com sucesso
        """
        return self.user_repository.invalidate_session(token)
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Busca todas as sessões ativas de um usuário
        
        Args:
            user_id: UUID do usuário
            
        Returns:
            Lista de sessões
        """
        if not validate_uuid(user_id):
            return []
            
        sessions = self.user_repository.get_user_sessions(user_id)
        
        return [
            {
                "id": session.id,
                "token": session.token,
                "expires_at": session.expires_at,
                "created_at": session.created_at,
                "is_active": session.is_active
            }
            for session in sessions
        ]
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca atividades de um usuário
        
        Args:
            user_id: UUID do usuário
            limit: Número máximo de atividades
            
        Returns:
            Lista de atividades
        """
        if not validate_uuid(user_id):
            return []
            
        activities = self.user_repository.get_user_activities(user_id, limit)
        
        return [
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "activity_metadata": activity.activity_metadata,
                "created_at": activity.created_at
            }
            for activity in activities
        ]
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Altera a senha do usuário
        
        Args:
            user_id: UUID do usuário
            current_password: Senha atual
            new_password: Nova senha
            
        Returns:
            True se alterada com sucesso
        """
        if not validate_uuid(user_id):
            return False
            
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return False
        
        # Verificar senha atual
        if not self._verify_password(current_password, user.password_hash):
            return False
        
        # Hash da nova senha
        new_password_hash = self._hash_password(new_password)
        
        # Atualizar senha
        updated_user = self.user_repository.update_user(user_id, password_hash=new_password_hash)
        if not updated_user:
            return False
        
        # Log da atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="password_changed",
            description="Senha alterada com sucesso"
        )
        
        return True
    
    def reset_password(self, email: str) -> bool:
        """
        Inicia processo de reset de senha
        
        Args:
            email: Email do usuário
            
        Returns:
            True se processo iniciado
        """
        user = self.user_repository.get_user_by_email(email)
        if not user:
            return False
        
        # Gerar token de reset (24 horas)
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # TODO: Implementar armazenamento do token de reset
        # TODO: Enviar email com link de reset
        
        # Log da atividade
        self.user_repository.create_activity(
            user_id=user.id,
            activity_type="password_reset_requested",
            description="Solicitação de reset de senha"
        )
        
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash da senha usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica se a senha está correta"""
        return self._hash_password(password) == password_hash
