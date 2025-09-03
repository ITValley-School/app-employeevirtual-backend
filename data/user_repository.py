"""
Repositório de usuários para o sistema EmployeeVirtual
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, cast, Date

from models.user_models import User, UserSession, UserActivity
from models.uuid_models import validate_uuid


class UserRepository:
    """Repositório para operações de dados de usuários"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD Usuários
    def create_user(self, name: str, email: str, password_hash: str, plan: str = "free") -> User:
        """Cria um novo usuário"""
        from models.uuid_models import generate_uuid
        
        db_user = User(
            id=generate_uuid(),  # Gerar UUID manualmente
            name=name,
            email=email,
            password_hash=password_hash,
            plan=plan
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID (UUID)"""
        if not validate_uuid(user_id):
            return None
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Atualiza dados do usuário"""
        if not validate_uuid(user_id):
            return None
            
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Remove usuário"""
        if not validate_uuid(user_id):
            return False
            
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista usuários com paginação"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def get_users_count(self) -> int:
        """Retorna total de usuários"""
        return self.db.query(User).count()
    
    # CRUD Sessões
    def create_session(self, user_id: str, token: str, expires_at: datetime) -> UserSession:
        """Cria uma nova sessão de usuário"""
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
        
        from models.uuid_models import generate_uuid
            
        db_session = UserSession(
            id=generate_uuid(),  # Gerar UUID manualmente
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session
    
    def get_session_by_token(self, token: str) -> Optional[UserSession]:
        """Busca sessão por token"""
        return self.db.query(UserSession).filter(
            and_(
                UserSession.token == token,
                UserSession.expires_at > datetime.utcnow(),
                UserSession.is_active == True
            )
        ).first()
    
    def invalidate_session(self, token: str) -> bool:
        """Invalida uma sessão"""
        session = self.db.query(UserSession).filter(UserSession.token == token).first()
        if not session:
            return False
        
        session.is_active = False
        self.db.commit()
        return True
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Busca todas as sessões de um usuário"""
        if not validate_uuid(user_id):
            return []
            
        return self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).all()
    
    def cleanup_expired_sessions(self) -> int:
        """Remove sessões expiradas"""
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at <= datetime.utcnow()
        ).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            self.db.delete(session)
        
        self.db.commit()
        return count
    
    # CRUD Atividades
    def create_activity(self, user_id: str, activity_type: str, description: str = None, metadata: dict = None) -> UserActivity:
        """Cria uma nova atividade do usuário"""
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
            
        activity_metadata = None
        if metadata:
            import json
            activity_metadata = json.dumps(metadata)
        
        from models.uuid_models import generate_uuid
        
        db_activity = UserActivity(
            id=generate_uuid(),  # Gerar UUID manualmente
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            activity_metadata=activity_metadata
        )
        self.db.add(db_activity)
        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[UserActivity]:
        """Busca atividades de um usuário"""
        if not validate_uuid(user_id):
            return []
            
        return self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(desc(UserActivity.created_at)).limit(limit).all()
    
    def get_activity_by_id(self, activity_id: str) -> Optional[UserActivity]:
        """Busca atividade por ID"""
        if not validate_uuid(activity_id):
            return None
            
        return self.db.query(UserActivity).filter(UserActivity.id == activity_id).first()
    
    def delete_activity(self, activity_id: str) -> bool:
        """Remove uma atividade"""
        if not validate_uuid(activity_id):
            return False
            
        activity = self.get_activity_by_id(activity_id)
        if not activity:
            return False
        
        self.db.delete(activity)
        self.db.commit()
        return True
    
    # Métodos de busca e filtros
    def search_users(self, search_term: str, limit: int = 20) -> List[User]:
        """Busca usuários por nome ou email"""
        search_pattern = f"%{search_term}%"
        return self.db.query(User).filter(
            or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    def get_users_by_plan(self, plan: str, limit: int = 100) -> List[User]:
        """Busca usuários por plano"""
        return self.db.query(User).filter(User.plan == plan).limit(limit).all()
    
    def get_users_by_status(self, status: str, limit: int = 100) -> List[User]:
        """Busca usuários por status"""
        return self.db.query(User).filter(User.status == status).limit(limit).all()
    
    def get_recent_users(self, days: int = 7, limit: int = 50) -> List[User]:
        """Busca usuários criados recentemente"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).filter(
            User.created_at >= cutoff_date
        ).order_by(desc(User.created_at)).limit(limit).all()
    
    def get_users_with_activity(self, days: int = 30, limit: int = 100) -> List[User]:
        """Busca usuários com atividade recente"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).join(UserActivity).filter(
            UserActivity.created_at >= cutoff_date
        ).distinct().limit(limit).all()
    
    # Métodos de estatísticas
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Retorna estatísticas de um usuário"""
        if not validate_uuid(user_id):
            return {}
            
        user = self.get_user_by_id(user_id)
        if not user:
            return {}
        
        # Contar sessões ativas
        active_sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).count()
        
        # Contar atividades
        total_activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).count()
        
        # Última atividade
        last_activity = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(desc(UserActivity.created_at)).first()
        
        return {
            "user_id": user_id,
            "name": user.name,
            "email": user.email,
            "plan": user.plan,
            "status": user.status,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "active_sessions": active_sessions,
            "total_activities": total_activities,
            "last_activity": last_activity.created_at if last_activity else None
        }
