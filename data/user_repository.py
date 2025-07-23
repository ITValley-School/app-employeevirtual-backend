"""
Repositório de usuários para o sistema EmployeeVirtual
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, cast, Date

from models.user_models import User, UserSession, UserActivity


class UserRepository:
    """Repositório para operações de dados de usuários"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD Usuários
    def create_user(self, name: str, email: str, password_hash: str, plan: str = "free") -> User:
        """Cria um novo usuário"""
        db_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            plan=plan
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Atualiza dados do usuário"""
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
    
    def delete_user(self, user_id: int) -> bool:
        """Remove usuário"""
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
    def create_session(self, user_id: int, token: str, expires_at: datetime) -> UserSession:
        """Cria uma nova sessão de usuário"""
        db_session = UserSession(
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
    
    def invalidate_user_sessions(self, user_id: int) -> bool:
        """Invalida todas as sessões de um usuário"""
        sessions = self.db.query(UserSession).filter(UserSession.user_id == user_id).all()
        for session in sessions:
            session.is_active = False
        
        self.db.commit()
        return True
    
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
    def create_activity(self, user_id: int, activity_type: str, description: str, 
                       activity_metadata: Optional[Dict[str, Any]] = None) -> UserActivity:
        """Cria um registro de atividade do usuário"""
        db_activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            activity_metadata=activity_metadata or "{}"
        )
        self.db.add(db_activity)
        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity
    
    def get_user_activities(self, user_id: int, limit: int = 50, offset: int = 0) -> List[UserActivity]:
        """Busca atividades do usuário"""
        return self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(desc(UserActivity.created_at)).offset(offset).limit(limit).all()
    
    def get_activities_by_type(self, user_id: int, activity_type: str, 
                              days: int = 30) -> List[UserActivity]:
        """Busca atividades por tipo nos últimos N dias"""
        since_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(UserActivity).filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == activity_type,
                UserActivity.created_at >= since_date
            )
        ).order_by(desc(UserActivity.created_at)).all()
    
    def get_daily_activity_count(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Busca contagem de atividades por dia"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            cast(UserActivity.created_at, Date).label('date'),
            func.count(UserActivity.id).label('count')
        ).filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.created_at >= since_date
            )
        ).group_by(
            cast(UserActivity.created_at, Date)
        ).order_by(desc('date')).all()
        
        return [{'date': result.date, 'count': result.count} for result in results]
    
    def get_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, int]:
        """Busca resumo de atividades por tipo"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            UserActivity.activity_type,
            func.count(UserActivity.id).label('count')
        ).filter(
            and_(
                UserActivity.user_id == user_id,
                UserActivity.created_at >= since_date
            )
        ).group_by(UserActivity.activity_type).all()
        
        return {result.activity_type: result.count for result in results}
    
    # Métricas e relatórios
    def get_user_metrics(self, user_id: int) -> Dict[str, Any]:
        """Busca métricas consolidadas do usuário"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {}
        
        # Atividades dos últimos 30 dias
        activity_summary = self.get_activity_summary(user_id, 30)
        daily_activities = self.get_daily_activity_count(user_id, 30)
        
        # Sessões ativas
        active_sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).count()
        
        return {
            'user_id': user_id,
            'name': user.name,
            'email': user.email,
            'plan': user.plan,
            'created_at': user.created_at,
            'last_login': user.last_login,
            'activity_summary': activity_summary,
            'daily_activities': daily_activities,
            'active_sessions': active_sessions,
            'total_activities': sum(activity_summary.values())
        }
