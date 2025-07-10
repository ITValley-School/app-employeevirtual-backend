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
from models.dashboard_models import UserMetrics


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
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        
        return {
            "user": user_response,
            "token": token,
            "expires_at": expires_at
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """
        Busca usuário por ID
        
        Args:
            user_id: ID do usuário
            
        Returns:
            UserResponse ou None se não encontrado
        """
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            plan=user.plan,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Atualiza dados do usuário
        
        Args:
            user_id: ID do usuário
            user_data: Dados para atualização
            
        Returns:
            UserResponse ou None se usuário não encontrado
        """
        # Verificar se email já está em uso por outro usuário
        if user_data.email:
            existing_user = self.user_repository.get_user_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email já está em uso por outro usuário")
        
        # Preparar dados para atualização
        update_data = {}
        if user_data.name is not None:
            update_data['name'] = user_data.name
        if user_data.email is not None:
            update_data['email'] = user_data.email
        if user_data.plan is not None:
            update_data['plan'] = user_data.plan
        if user_data.password is not None:
            update_data['password_hash'] = self._hash_password(user_data.password)
        
        # Atualizar usuário
        updated_user = self.user_repository.update_user(user_id, **update_data)
        if not updated_user:
            return None
        
        # Log da atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="user_updated",
            description="Dados do usuário atualizados"
        )
        
        return UserResponse(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            plan=updated_user.plan,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            last_login=updated_user.last_login
        )
    
    def delete_user(self, user_id: int) -> bool:
        """
        Remove um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se removido com sucesso
        """
        # Invalidar todas as sessões do usuário
        self.user_repository.invalidate_user_sessions(user_id)
        
        # Remover usuário
        return self.user_repository.delete_user(user_id)
    
    def create_session(self, user_id: int, expires_in_hours: int = 24) -> str:
        """
        Cria uma sessão para o usuário
        
        Args:
            user_id: ID do usuário
            expires_in_hours: Duração da sessão em horas
            
        Returns:
            Token da sessão
        """
        # Gerar token único
        token = self._generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        # Criar sessão
        self.user_repository.create_session(user_id, token, expires_at)
        
        # Log da atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="session_created",
            description="Nova sessão criada"
        )
        
        return token
    
    def validate_session(self, token: str) -> Optional[UserResponse]:
        """
        Valida um token de sessão
        
        Args:
            token: Token da sessão
            
        Returns:
            UserResponse se sessão válida, None caso contrário
        """
        session = self.user_repository.get_session_by_token(token)
        if not session:
            return None
        
        user = self.user_repository.get_user_by_id(session.user_id)
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            plan=user.plan,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
    
    def invalidate_session(self, token: str) -> bool:
        """
        Invalida uma sessão
        
        Args:
            token: Token da sessão
            
        Returns:
            True se invalidada com sucesso
        """
        return self.user_repository.invalidate_session(token)
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove sessões expiradas
        
        Returns:
            Número de sessões removidas
        """
        return self.user_repository.cleanup_expired_sessions()
    
    def get_user_activities(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Busca atividades do usuário
        
        Args:
            user_id: ID do usuário
            limit: Limite de atividades
            offset: Deslocamento para paginação
            
        Returns:
            Lista de atividades
        """
        activities = self.user_repository.get_user_activities(user_id, limit, offset)
        
        return [
            {
                'id': activity.id,
                'activity_type': activity.activity_type,
                'description': activity.description,
                'activity_metadata': activity.activity_metadata,
                'created_at': activity.created_at
            }
            for activity in activities
        ]
    
    def get_user_metrics(self, user_id: int) -> UserMetrics:
        """
        Busca métricas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Métricas do usuário
        """
        metrics_data = self.user_repository.get_user_metrics(user_id)
        
        if not metrics_data:
            raise ValueError("Usuário não encontrado")
        
        return UserMetrics(
            user_id=metrics_data['user_id'],
            name=metrics_data['name'],
            email=metrics_data['email'],
            plan=metrics_data['plan'],
            created_at=metrics_data['created_at'],
            last_login=metrics_data['last_login'],
            activity_summary=metrics_data['activity_summary'],
            daily_activities=metrics_data['daily_activities'],
            active_sessions=metrics_data['active_sessions'],
            total_activities=metrics_data['total_activities']
        )
    
    def log_user_activity(self, user_id: int, activity_type: str, description: str,
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Registra uma atividade do usuário
        
        Args:
            user_id: ID do usuário
            activity_type: Tipo da atividade
            description: Descrição da atividade
            metadata: Metadados adicionais
            
        Returns:
            True se registrada com sucesso
        """
        try:
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                activity_metadata=metadata
            )
            return True
        except Exception:
            return False
    
    def get_user_by_token(self, token: str) -> Optional[UserResponse]:
        """
        Busca usuário por token de sessão
        
        Args:
            token: Token de sessão
            
        Returns:
            UserResponse ou None se token inválido
        """
        session = self.user_repository.get_session_by_token(token)
        if not session:
            return None
        
        user = self.user_repository.get_user_by_id(session.user_id)
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            plan=user.plan,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
    
    def logout_user(self, token: str) -> bool:
        """
        Faz logout do usuário (invalida token)
        
        Args:
            token: Token de sessão
            
        Returns:
            True se logout realizado com sucesso
        """
        success = self.user_repository.invalidate_session(token)
        
        if success:
            # Tentar buscar usuário para log (pode falhar se token inválido)
            try:
                session = self.user_repository.get_session_by_token(token)
                if session:
                    self.user_repository.create_activity(
                        user_id=session.user_id,
                        activity_type="user_logout",
                        description="Logout realizado"
                    )
            except Exception:
                pass
        
        return success
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Busca estatísticas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Estatísticas do usuário
        """
        return self.user_repository.get_user_metrics(user_id)
    
    # Métodos privados para hash de senha e tokens
    def _hash_password(self, password: str) -> str:
        """Gera hash da senha"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica senha contra hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_check.hex() == stored_hash
        except Exception:
            return False
    
    def _generate_session_token(self) -> str:
        """Gera token único para sessão"""
        return secrets.token_urlsafe(32)
