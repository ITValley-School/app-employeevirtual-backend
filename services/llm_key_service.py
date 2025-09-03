"""
Serviço para gerenciamento de chaves LLM
"""
import os
import base64
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.orm import Session

from models.llm_models import (
    SystemLLMKey, UserLLMKey, LLMProvider,
    SystemLLMKeyCreate, SystemLLMKeyUpdate,
    UserLLMKeyCreate, UserLLMKeyUpdate,
    LLMKeyValidationRequest, LLMKeyValidationResponse
)
from data.llm_repository import LLMKeyRepository
from auth.dependencies import get_current_user

class LLMKeyManager:
    """Gerenciador de chaves LLM com criptografia"""
    
    def __init__(self):
        self._cipher_suite = None
        self._initialize_cipher()
    
    def _initialize_cipher(self):
        """Inicializa o sistema de criptografia"""
        try:
            # Obter chave de criptografia das variáveis de ambiente
            encryption_key = os.getenv('ENCRYPTION_KEY')
            
            if not encryption_key:
                # Gerar chave se não existir
                encryption_key = Fernet.generate_key()
                print(f"⚠️ ENCRYPTION_KEY não encontrada. Nova chave gerada: {encryption_key.decode()}")
                print("⚠️ Adicione esta chave às variáveis de ambiente!")
            
            # Converter para bytes se for string
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            self._cipher_suite = Fernet(encryption_key)
            
        except Exception as e:
            print(f"❌ Erro ao inicializar criptografia: {e}")
            raise
    
    def encrypt_key(self, api_key: str) -> str:
        """Criptografa uma chave API"""
        if not self._cipher_suite:
            raise RuntimeError("Sistema de criptografia não inicializado")
        
        try:
            encrypted_bytes = self._cipher_suite.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            print(f"❌ Erro ao criptografar chave: {e}")
            raise
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Descriptografa uma chave API"""
        if not self._cipher_suite:
            raise RuntimeError("Sistema de criptografia não inicializado")
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted_bytes = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"❌ Erro ao descriptografar chave: {e}")
            raise

class LLMKeyService:
    """Serviço para operações com chaves LLM"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = LLMKeyRepository(db)
        self.key_manager = LLMKeyManager()
    
    # Métodos para chaves do sistema (admin)
    async def create_system_key(self, key_data: SystemLLMKeyCreate) -> SystemLLMKey:
        """Cria uma nova chave LLM do sistema"""
        try:
            # Criptografar a chave API
            encrypted_key = self.key_manager.encrypt_key(key_data.api_key)
            
            # Criar objeto da chave
            db_key = SystemLLMKey(
                provider=key_data.provider,
                api_key=encrypted_key,
                usage_limit=key_data.usage_limit,
                is_active=key_data.is_active
            )
            
            # Salvar no banco
            return self.repository.create_system_key(db_key)
            
        except Exception as e:
            print(f"❌ Erro ao criar chave do sistema: {e}")
            raise
    
    async def update_system_key(self, key_id: str, key_data: SystemLLMKeyUpdate) -> Optional[SystemLLMKey]:
        """Atualiza uma chave LLM do sistema"""
        try:
            # Buscar chave existente
            existing_key = self.repository.get_system_key_by_id(key_id)
            if not existing_key:
                return None
            
            # Atualizar campos
            if key_data.api_key is not None:
                encrypted_key = self.key_manager.encrypt_key(key_data.api_key)
                existing_key.api_key = encrypted_key
            
            if key_data.usage_limit is not None:
                existing_key.usage_limit = key_data.usage_limit
            
            if key_data.is_active is not None:
                existing_key.is_active = key_data.is_active
            
            existing_key.updated_at = datetime.utcnow()
            
            # Salvar alterações
            return self.repository.update_system_key(existing_key)
            
        except Exception as e:
            print(f"❌ Erro ao atualizar chave do sistema: {e}")
            raise
    
    async def get_system_keys(self) -> List[SystemLLMKey]:
        """Lista todas as chaves LLM do sistema"""
        return self.repository.get_system_keys()
    
    async def get_system_key_by_provider(self, provider: LLMProvider) -> Optional[SystemLLMKey]:
        """Busca chave do sistema por provedor"""
        return self.repository.get_system_key_by_provider(provider)
    
    # Métodos para chaves do usuário
    async def create_user_key(self, user_id: str, key_data: UserLLMKeyCreate) -> UserLLMKey:
        """Cria uma nova chave LLM do usuário"""
        try:
            # Criptografar a chave API
            encrypted_key = self.key_manager.encrypt_key(key_data.api_key)
            
            # Criar objeto da chave
            db_key = UserLLMKey(
                user_id=user_id,
                provider=key_data.provider,
                api_key=encrypted_key,
                usage_limit=key_data.usage_limit,
                is_active=key_data.is_active
            )
            
            # Salvar no banco
            return self.repository.create_user_key(db_key)
            
        except Exception as e:
            print(f"❌ Erro ao criar chave do usuário: {e}")
            raise
    
    async def update_user_key(self, key_id: str, user_id: str, key_data: UserLLMKeyUpdate) -> Optional[UserLLMKey]:
        """Atualiza uma chave LLM do usuário"""
        try:
            # Buscar chave existente
            existing_key = self.repository.get_user_key_by_id(key_id)
            if not existing_key or existing_key.user_id != user_id:
                return None
            
            # Atualizar campos
            if key_data.api_key is not None:
                encrypted_key = self.key_manager.encrypt_key(key_data.api_key)
                existing_key.api_key = encrypted_key
            
            if key_data.usage_limit is not None:
                existing_key.usage_limit = key_data.usage_limit
            
            if key_data.is_active is not None:
                existing_key.is_active = key_data.is_active
            
            existing_key.updated_at = datetime.utcnow()
            
            # Salvar alterações
            return self.repository.update_user_key(existing_key)
            
        except Exception as e:
            print(f"❌ Erro ao atualizar chave do usuário: {e}")
            raise
    
    async def get_user_keys(self, user_id: str) -> List[UserLLMKey]:
        """Lista todas as chaves LLM do usuário"""
        return self.repository.get_user_keys_by_user_id(user_id)
    
    async def get_user_key_by_id(self, key_id: str, user_id: str) -> Optional[UserLLMKey]:
        """Busca chave do usuário por ID"""
        key = self.repository.get_user_key_by_id(key_id)
        if key and key.user_id == user_id:
            return key
        return None
    
    async def delete_user_key(self, key_id: str, user_id: str) -> bool:
        """Remove uma chave LLM do usuário"""
        key = self.repository.get_user_key_by_id(key_id)
        if key and key.user_id == user_id:
            return self.repository.delete_user_key(key_id)
        return False
    
    # Validação de chaves
    async def validate_api_key(self, validation_request: LLMKeyValidationRequest) -> LLMKeyValidationResponse:
        """Valida uma chave API com o provedor"""
        try:
            # Aqui você implementaria a validação real com cada provedor
            # Por enquanto, vamos simular uma validação básica
            
            provider = validation_request.provider
            api_key = validation_request.api_key
            
            # Validação básica (você pode expandir isso)
            if len(api_key) < 10:
                return LLMKeyValidationResponse(
                    is_valid=False,
                    provider=provider,
                    message="Chave API muito curta",
                    model_info=None
                )
            
            # Simular validação com provedor
            is_valid = await self._validate_with_provider(provider, api_key)
            
            if is_valid:
                return LLMKeyValidationResponse(
                    is_valid=True,
                    provider=provider,
                    message="Chave API válida",
                    model_info={"provider": provider, "status": "active"}
                )
            else:
                return LLMKeyValidationResponse(
                    is_valid=False,
                    provider=provider,
                    message="Chave API inválida ou inativa",
                    model_info=None
                )
                
        except Exception as e:
            return LLMKeyValidationResponse(
                is_valid=False,
                provider=validation_request.provider,
                message=f"Erro na validação: {str(e)}",
                model_info=None
            )
    
    async def _validate_with_provider(self, provider: LLMProvider, api_key: str) -> bool:
        """Valida chave com o provedor específico"""
        # Aqui você implementaria a validação real
        # Por exemplo, para OpenAI:
        if provider == LLMProvider.OPENAI:
            try:
                # import openai
                # openai.api_key = api_key
                # models = openai.Model.list()
                # return len(models.data) > 0
                return True  # Simulação
            except:
                return False
        
        # Para outros provedores, implementar validação similar
        return True  # Simulação para outros provedores
    
    # Métodos de uso e estatísticas
    async def get_key_for_agent(self, agent_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtém a chave apropriada para execução de um agente"""
        try:
            # Buscar agente
            from models.agent_models import Agent
            agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
            
            if not agent:
                return None
            
            # Verificar se usa chave do sistema
            if agent.use_system_key and agent.system_key_provider:
                system_key = await self.get_system_key_by_provider(agent.system_key_provider)
                if system_key and system_key.is_active:
                    return {
                        "type": "system",
                        "provider": system_key.provider,
                        "api_key": self.key_manager.decrypt_key(system_key.api_key),
                        "key_id": system_key.id
                    }
            
            # Verificar se usa chave do usuário
            elif agent.user_key_id:
                user_key = await self.get_user_key_by_id(agent.user_key_id, user_id)
                if user_key and user_key.is_active:
                    return {
                        "type": "user",
                        "provider": user_key.provider,
                        "api_key": self.key_manager.decrypt_key(user_key.api_key),
                        "key_id": user_key.id
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter chave para agente: {e}")
            return None
    
    async def update_key_usage(self, key_id: str, usage_amount: float, key_type: str = "user"):
        """Atualiza o uso de uma chave"""
        try:
            if key_type == "system":
                self.repository.update_system_key_usage(key_id, usage_amount)
            else:
                self.repository.update_user_key_usage(key_id, usage_amount)
        except Exception as e:
            print(f"❌ Erro ao atualizar uso da chave: {e}")
    
    async def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtém estatísticas de uso das chaves do usuário"""
        try:
            user_keys = await self.get_user_keys(user_id)
            system_keys = await self.get_system_keys()
            
            stats = {
                "user_keys": [],
                "system_keys": [],
                "total_usage": 0
            }
            
            # Estatísticas das chaves do usuário
            for key in user_keys:
                usage_percentage = 0
                if key.usage_limit:
                    usage_percentage = (key.current_usage / key.usage_limit) * 100
                
                stats["user_keys"].append({
                    "provider": key.provider,
                    "current_usage": float(key.current_usage),
                    "usage_limit": float(key.usage_limit) if key.usage_limit else None,
                    "usage_percentage": round(usage_percentage, 2),
                    "last_used": key.last_used,
                    "is_active": key.is_active
                })
                
                stats["total_usage"] += float(key.current_usage)
            
            # Estatísticas das chaves do sistema
            for key in system_keys:
                usage_percentage = 0
                if key.usage_limit:
                    usage_percentage = (key.current_usage / key.usage_limit) * 100
                
                stats["system_keys"].append({
                    "provider": key.provider,
                    "current_usage": float(key.current_usage),
                    "usage_limit": float(key.usage_limit) if key.usage_limit else None,
                    "usage_percentage": round(usage_percentage, 2),
                    "last_used": key.last_used,
                    "is_active": key.is_active
                })
            
            return stats
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas de uso: {e}")
            return {}
