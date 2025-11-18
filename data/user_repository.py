"""
Repositório de usuários para o sistema EmployeeVirtual
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, cast, Date

from data.entities.user_entities import UserEntity, UserSessionEntity, UserActivityEntity
# Validação de UUID local
def validate_uuid(uuid_string: str) -> bool:
    """Valida se string é um UUID válido (aceita com ou sem hífens)"""
    if not uuid_string:
        return False
    
    # UUID sem hífens: 32 caracteres
    # UUID com hífens: 36 caracteres (8-4-4-4-12)
    if len(uuid_string) == 32:
        try:
            # Verifica se é hexadecimal
            int(uuid_string, 16)
            return True
        except ValueError:
            return False
    elif len(uuid_string) == 36:
        # Verifica formato com hífens: 8-4-4-4-12
        import re
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_string, re.IGNORECASE))
    
    return False


class UserRepository:
    """Repositório para operações de dados de usuários"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD Usuários
    def create_user(self, name: str, email: str, password_hash: str, plan: str = "free") -> UserEntity:
        """Cria um novo usuário"""
        # Geração de UUID local
        import uuid
        def generate_uuid():
            return uuid.uuid4().hex
        
        db_user = UserEntity(
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
    
    def get_user_by_id(self, user_id: str) -> Optional[UserEntity]:
        """Busca usuário por ID (UUID)"""
        if not validate_uuid(user_id):
            return None
        return self.db.query(UserEntity).filter(UserEntity.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        """Busca usuário por email"""
        return self.db.query(UserEntity).filter(UserEntity.email == email).first()
    
    def exists_email(self, email: str) -> bool:
        """Verifica se email já existe"""
        user = self.db.query(UserEntity).filter(UserEntity.email == email).first()
        return user is not None
    
    def add(self, entity: UserEntity) -> None:
        """Adiciona entidade e faz commit"""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
    
    def update(self, entity: UserEntity) -> None:
        """Atualiza entidade e faz commit"""
        self.db.merge(entity)
        self.db.commit()
    
    def update_user(self, user_id: str, **kwargs) -> Optional[UserEntity]:
        """Atualiza dados do usuário"""
        if not validate_uuid(user_id):
            return None
            
        UserEntity = self.get_user_by_id(user_id)
        if not UserEntity:
            return None
        
        for key, value in kwargs.items():
            if hasattr(UserEntity, key) and value is not None:
                setattr(UserEntity, key, value)
        
        UserEntity.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(UserEntity)
        return UserEntity
    
    def delete_user(self, user_id: str) -> bool:
        """Remove usuário"""
        if not validate_uuid(user_id):
            return False
            
        UserEntity = self.get_user_by_id(user_id)
        if not UserEntity:
            return False
        
        self.db.delete(UserEntity)
        self.db.commit()
        return True
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        """Lista usuários com paginação"""
        return self.db.query(UserEntity).offset(skip).limit(limit).all()
    
    def get_users_count(self) -> int:
        """Retorna total de usuários"""
        return self.db.query(UserEntity).count()
    
    # CRUD Sessões
    def create_session(self, user_id: str, token: str, expires_at: datetime) -> UserSessionEntity:
        """Cria uma nova sessão de usuário"""
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
        
        # Geração de UUID local
        import uuid
        def generate_uuid():
            return uuid.uuid4().hex
            
        db_session = UserSessionEntity(
            id=generate_uuid(),  # Gerar UUID manualmente
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session
    
    def get_session_by_token(self, token: str) -> Optional[UserSessionEntity]:
        """Busca sessão por token"""
        return self.db.query(UserSessionEntity).filter(
            and_(
                UserSessionEntity.token == token,
                UserSessionEntity.expires_at > datetime.utcnow(),
                UserSessionEntity.is_active == True
            )
        ).first()
    
    def invalidate_session(self, token: str) -> bool:
        """Invalida uma sessão"""
        session = self.db.query(UserSessionEntity).filter(UserSessionEntity.token == token).first()
        if not session:
            return False
        
        session.is_active = False
        self.db.commit()
        return True
    
    def get_user_sessions(self, user_id: str) -> List[UserSessionEntity]:
        """Busca todas as sessões de um usuário"""
        if not validate_uuid(user_id):
            return []
            
        return self.db.query(UserSessionEntity).filter(
            and_(
                UserSessionEntity.user_id == user_id,
                UserSessionEntity.is_active == True
            )
        ).all()
    
    def cleanup_expired_sessions(self) -> int:
        """Remove sessões expiradas"""
        expired_sessions = self.db.query(UserSessionEntity).filter(
            UserSessionEntity.expires_at <= datetime.utcnow()
        ).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            self.db.delete(session)
        
        self.db.commit()
        return count
    
    # CRUD Atividades
    def create_activity(self, user_id: str, activity_type: str, description: str = None, metadata: dict = None) -> UserActivityEntity:
        """Cria uma nova atividade do usuário"""
        if not validate_uuid(user_id):
            raise ValueError("Invalid user_id UUID")
            
        activity_metadata = None
        if metadata:
            import json
            activity_metadata = json.dumps(metadata)
        
        # Geração de UUID local
        import uuid
        def generate_uuid():
            return uuid.uuid4().hex
        
        db_activity = UserActivityEntity(
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
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[UserActivityEntity]:
        """Busca atividades de um usuário"""
        if not validate_uuid(user_id):
            return []
            
        return self.db.query(UserActivityEntity).filter(
            UserActivityEntity.user_id == user_id
        ).order_by(desc(UserActivityEntity.created_at)).limit(limit).all()
    
    def get_activity_by_id(self, activity_id: str) -> Optional[UserActivityEntity]:
        """Busca atividade por ID"""
        if not validate_uuid(activity_id):
            return None
            
        return self.db.query(UserActivityEntity).filter(UserActivityEntity.id == activity_id).first()
    
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
    def search_users(self, search_term: str, limit: int = 20) -> List[UserEntity]:
        """Busca usuários por nome ou email"""
        search_pattern = f"%{search_term}%"
        return self.db.query(UserEntity).filter(
            or_(
                UserEntity.name.ilike(search_pattern),
                UserEntity.email.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    def get_users_by_plan(self, plan: str, limit: int = 100) -> List[UserEntity]:
        """Busca usuários por plano"""
        return self.db.query(UserEntity).filter(UserEntity.plan == plan).limit(limit).all()
    
    def get_users_by_status(self, status: str, limit: int = 100) -> List[UserEntity]:
        """Busca usuários por status"""
        return self.db.query(UserEntity).filter(UserEntity.status == status).limit(limit).all()
    
    def get_recent_users(self, days: int = 7, limit: int = 50) -> List[UserEntity]:
        """Busca usuários criados recentemente"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(UserEntity).filter(
            UserEntity.created_at >= cutoff_date
        ).order_by(desc(UserEntity.created_at)).limit(limit).all()
    
    def get_users_with_activity(self, days: int = 30, limit: int = 100) -> List[UserEntity]:
        """Busca usuários com atividade recente"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(UserEntity).join(UserActivityEntity).filter(
            UserActivityEntity.created_at >= cutoff_date
        ).distinct().limit(limit).all()
    
    # Métodos de estatísticas
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Retorna estatísticas de um usuário"""
        if not validate_uuid(user_id):
            return {}
            
        UserEntity = self.get_user_by_id(user_id)
        if not UserEntity:
            return {}
        
        # Contar sessões ativas
        active_sessions = self.db.query(UserSessionEntity).filter(
            and_(
                UserSessionEntity.user_id == user_id,
                UserSessionEntity.is_active == True,
                UserSessionEntity.expires_at > datetime.utcnow()
            )
        ).count()
        
        # Contar atividades
        total_activities = self.db.query(UserActivityEntity).filter(
            UserActivityEntity.user_id == user_id
        ).count()
        
        # Última atividade
        last_activity = self.db.query(UserActivityEntity).filter(
            UserActivityEntity.user_id == user_id
        ).order_by(desc(UserActivityEntity.created_at)).first()
    
        return {
            "user_id": user_id,
            "name": UserEntity.name,
            "email": UserEntity.email,
            "plan": UserEntity.plan,
            "status": UserEntity.status,
            "created_at": UserEntity.created_at,
            "last_login": UserEntity.last_login,
            "active_sessions": active_sessions,
            "total_activities": total_activities,
            "last_activity": last_activity.created_at if last_activity else None
        }
