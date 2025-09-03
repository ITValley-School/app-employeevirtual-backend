"""
Repositório para operações de chaves LLM no banco de dados
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta

from models.llm_models import SystemLLMKey, UserLLMKey, LLMProvider
from models.uuid_models import validate_uuid

class LLMKeyRepository:
    """Repositório para operações de chaves LLM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Métodos para chaves do sistema
    def create_system_key(self, system_key: SystemLLMKey) -> SystemLLMKey:
        """Cria uma nova chave LLM do sistema"""
        try:
            self.db.add(system_key)
            self.db.commit()
            self.db.refresh(system_key)
            return system_key
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao criar chave do sistema: {e}")
            raise
    
    def get_system_key_by_id(self, key_id: str) -> Optional[SystemLLMKey]:
        """Busca chave do sistema por ID"""
        try:
            validate_uuid(key_id)
            return self.db.query(SystemLLMKey).filter(SystemLLMKey.id == key_id).first()
        except Exception as e:
            print(f"❌ Erro ao buscar chave do sistema: {e}")
            return None
    
    def get_system_key_by_provider(self, provider: LLMProvider) -> Optional[SystemLLMKey]:
        """Busca chave do sistema por provedor"""
        try:
            return self.db.query(SystemLLMKey).filter(
                and_(
                    SystemLLMKey.provider == provider,
                    SystemLLMKey.is_active == True
                )
            ).first()
        except Exception as e:
            print(f"❌ Erro ao buscar chave do sistema por provedor: {e}")
            return None
    
    def get_system_keys(self) -> List[SystemLLMKey]:
        """Lista todas as chaves LLM do sistema"""
        try:
            return self.db.query(SystemLLMKey).order_by(SystemLLMKey.provider).all()
        except Exception as e:
            print(f"❌ Erro ao listar chaves do sistema: {e}")
            return []
    
    def update_system_key(self, system_key: SystemLLMKey) -> Optional[SystemLLMKey]:
        """Atualiza uma chave LLM do sistema"""
        try:
            system_key.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(system_key)
            return system_key
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao atualizar chave do sistema: {e}")
            return None
    
    def update_system_key_usage(self, key_id: str, usage_amount: float) -> bool:
        """Atualiza o uso de uma chave do sistema"""
        try:
            validate_uuid(key_id)
            key = self.get_system_key_by_id(key_id)
            if key:
                key.current_usage += usage_amount
                key.last_used = datetime.utcnow()
                key.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao atualizar uso da chave do sistema: {e}")
            return False
    
    # Métodos para chaves do usuário
    def create_user_key(self, user_key: UserLLMKey) -> UserLLMKey:
        """Cria uma nova chave LLM do usuário"""
        try:
            self.db.add(user_key)
            self.db.commit()
            self.db.refresh(user_key)
            return user_key
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao criar chave do usuário: {e}")
            raise
    
    def get_user_key_by_id(self, key_id: str) -> Optional[UserLLMKey]:
        """Busca chave do usuário por ID"""
        try:
            validate_uuid(key_id)
            return self.db.query(UserLLMKey).filter(UserLLMKey.id == key_id).first()
        except Exception as e:
            print(f"❌ Erro ao buscar chave do usuário: {e}")
            return None
    
    def get_user_keys_by_user_id(self, user_id: str) -> List[UserLLMKey]:
        """Lista todas as chaves LLM de um usuário"""
        try:
            validate_uuid(user_id)
            return self.db.query(UserLLMKey).filter(
                UserLLMKey.user_id == user_id
            ).order_by(UserLLMKey.provider).all()
        except Exception as e:
            print(f"❌ Erro ao listar chaves do usuário: {e}")
            return []
    
    def update_user_key(self, user_key: UserLLMKey) -> Optional[UserLLMKey]:
        """Atualiza uma chave LLM do usuário"""
        try:
            user_key.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user_key)
            return user_key
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao atualizar chave do usuário: {e}")
            return None
    
    def update_user_key_usage(self, key_id: str, usage_amount: float) -> bool:
        """Atualiza o uso de uma chave do usuário"""
        try:
            validate_uuid(key_id)
            key = self.get_user_key_by_id(key_id)
            if key:
                key.current_usage += usage_amount
                key.last_used = datetime.utcnow()
                key.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao atualizar uso da chave do usuário: {e}")
            return False
    
    def delete_user_key(self, key_id: str) -> bool:
        """Remove uma chave LLM do usuário"""
        try:
            validate_uuid(key_id)
            key = self.get_user_key_by_id(key_id)
            if key:
                self.db.delete(key)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erro ao remover chave do usuário: {e}")
            return False
