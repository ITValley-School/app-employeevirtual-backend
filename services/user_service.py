"""
Serviço de usuários para o sistema EmployeeVirtual
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from models.user_models import User, UserSession, UserActivity, UserCreate, UserUpdate, UserResponse, UserLogin
from models.dashboard_models import UserMetrics


class UserService:
    """Serviço para gerenciamento de usuários"""
    
    def __init__(self, db: Session):
        self.db = db
    
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
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email já está em uso")
        
        # Hash da senha
        password_hash = self._hash_password(user_data.password)
        
        # Criar usuário
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            plan=user_data.plan
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Registrar atividade
        self._log_activity(db_user.id, "user_created", "Usuário criado no sistema")
        
        return UserResponse.from_orm(db_user)
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """
        Autentica um usuário
        
        Args:
            login_data: Dados de login
            
        Returns:
            Dict com dados do usuário e token, ou None se inválido
        """
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not self._verify_password(login_data.password, user.password_hash):
            return None
        
        if user.status != "active":
            raise ValueError("Usuário inativo ou suspenso")
        
        # Gerar token de sessão
        token = self._generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=7)  # Token válido por 7 dias
        
        # Criar sessão
        session = UserSession(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        self.db.add(session)
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        
        self.db.commit()
        
        # Registrar atividade
        self._log_activity(user.id, "user_login", "Usuário fez login no sistema")
        
        return {
            "user": UserResponse.from_orm(user),
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
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        return UserResponse.from_orm(user)
    
    def get_user_by_token(self, token: str) -> Optional[UserResponse]:
        """
        Busca usuário por token de sessão
        
        Args:
            token: Token de sessão
            
        Returns:
            UserResponse ou None se token inválido
        """
        session = self.db.query(UserSession).filter(
            and_(
                UserSession.token == token,
                UserSession.expires_at > datetime.utcnow(),
                UserSession.is_active == True
            )
        ).first()
        
        if not session:
            return None
        
        user = self.db.query(User).filter(User.id == session.user_id).first()
        if not user or user.status != "active":
            return None
        
        return UserResponse.from_orm(user)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Atualiza dados do usuário
        
        Args:
            user_id: ID do usuário
            user_data: Dados a serem atualizados
            
        Returns:
            UserResponse atualizado ou None se não encontrado
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Atualizar campos fornecidos
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        # Registrar atividade
        self._log_activity(user_id, "user_updated", f"Usuário atualizou dados: {list(update_data.keys())}")
        
        return UserResponse.from_orm(user)
    
    def logout_user(self, token: str) -> bool:
        """
        Faz logout do usuário (invalida token)
        
        Args:
            token: Token de sessão
            
        Returns:
            True se logout bem-sucedido
        """
        session = self.db.query(UserSession).filter(UserSession.token == token).first()
        if not session:
            return False
        
        session.is_active = False
        self.db.commit()
        
        # Registrar atividade
        self._log_activity(session.user_id, "user_logout", "Usuário fez logout do sistema")
        
        return True
    
    def get_user_activities(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca atividades do usuário
        
        Args:
            user_id: ID do usuário
            limit: Limite de atividades
            
        Returns:
            Lista de atividades
        """
        activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "created_at": activity.created_at
            }
            for activity in activities
        ]
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Busca estatísticas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com estatísticas
        """
        from models.agent_models import Agent
        from models.flow_models import Flow
        from models.chat_models import Conversation
        
        # Contar agentes
        total_agents = self.db.query(Agent).filter(Agent.user_id == user_id).count()
        
        # Contar flows
        total_flows = self.db.query(Flow).filter(Flow.user_id == user_id).count()
        
        # Contar conversações
        total_conversations = self.db.query(Conversation).filter(Conversation.user_id == user_id).count()
        
        # Buscar métricas do dia atual
        today = datetime.utcnow().date()
        today_metrics = self.db.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date == today
            )
        ).first()
        
        executions_today = today_metrics.agent_executions + today_metrics.flow_executions if today_metrics else 0
        time_saved_today = today_metrics.time_saved if today_metrics else 0.0
        
        return {
            "total_agents": total_agents,
            "total_flows": total_flows,
            "total_conversations": total_conversations,
            "executions_today": executions_today,
            "time_saved_today": time_saved_today
        }
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove sessões expiradas
        
        Returns:
            Número de sessões removidas
        """
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_sessions)
        
        for session in expired_sessions:
            self.db.delete(session)
        
        self.db.commit()
        
        return count
    
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
            return stored_hash == password_hash_check.hex()
        except:
            return False
    
    def _generate_session_token(self) -> str:
        """Gera token de sessão único"""
        return secrets.token_urlsafe(32)
    
    def _log_activity(self, user_id: int, activity_type: str, description: str, metadata: Optional[Dict] = None):
        """Registra atividade do usuário"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            activity_metadata=str(metadata) if metadata else None
        )
        
        self.db.add(activity)
        # Não fazer commit aqui, deixar para o método principal

