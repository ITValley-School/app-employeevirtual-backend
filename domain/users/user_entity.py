"""
Entidade de usuário - Coração do domínio
Seguindo padrão IT Valley Architecture
"""
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime
from uuid import uuid4


@dataclass
class UserEntity:
    """
    Entidade de usuário - Coração do domínio
    Contém apenas dados e comportamentos essenciais
    """
    id: str
    name: str
    email: str
    password_hash: str
    plan: str = "free"
    status: str = "active"
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def activate(self) -> None:
        """
        Ativa o usuário
        """
        if self.status == "suspended":
            raise ValueError("Usuário suspenso não pode ser ativado")
        self.status = "active"
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """
        Desativa o usuário
        """
        self.status = "inactive"
        self.updated_at = datetime.utcnow()
    
    def suspend(self) -> None:
        """
        Suspende o usuário
        """
        self.status = "suspended"
        self.updated_at = datetime.utcnow()
    
    def update_last_login(self) -> None:
        """
        Atualiza último login
        """
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def change_plan(self, new_plan: str) -> None:
        """
        Altera plano do usuário
        
        Args:
            new_plan: Novo plano
            
        Raises:
            ValueError: Se plano inválido
        """
        valid_plans = ["free", "basic", "pro", "enterprise"]
        if new_plan not in valid_plans:
            raise ValueError(f"Plano inválido: {new_plan}")
        
        self.plan = new_plan
        self.updated_at = datetime.utcnow()
    
    def apply_update_from_any(self, data: Any) -> None:
        """
        Aplica atualizações de qualquer fonte de dados
        Método genérico para aplicar mudanças
        
        Args:
            data: Dados para atualização (dict, DTO, etc.)
        """
        # Helper para extrair dados de forma segura
        def _get(data: Any, key: str, default=None):
            if hasattr(data, key):
                return getattr(data, key)
            elif isinstance(data, dict):
                return data.get(key, default)
            return default
        
        # Aplica atualizações se os dados forem válidos
        new_name = _get(data, "name")
        if new_name and len(new_name.strip()) >= 2:
            self.name = new_name.strip()
        
        new_email = _get(data, "email")
        if new_email and "@" in new_email:
            self.email = new_email.strip()
        
        new_plan = _get(data, "plan")
        if new_plan:
            self.change_plan(new_plan)
        
        new_status = _get(data, "status")
        if new_status:
            self.status = new_status
        
        # Sempre atualiza timestamp
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """
        Verifica se usuário está ativo
        
        Returns:
            bool: True se ativo
        """
        return self.status == "active"
    
    def is_premium(self) -> bool:
        """
        Verifica se usuário tem plano premium
        
        Returns:
            bool: True se premium
        """
        return self.plan in ["pro", "enterprise"]
    
    def can_create_agents(self) -> bool:
        """
        Verifica se usuário pode criar agentes
        
        Returns:
            bool: True se pode criar
        """
        return self.is_active() and self.plan != "free"
    
    def get_id(self) -> str:
        """
        Retorna o ID do usuário
        """
        return self.id
    
    def get_email(self) -> str:
        """
        Retorna o email do usuário
        """
        return self.email
    
    def get_name(self) -> str:
        """
        Retorna o nome do usuário
        """
        return self.name
    
    def get_status(self) -> str:
        """
        Retorna o status do usuário
        """
        return self.status
    
    def get_plan(self) -> str:
        """
        Retorna o plano do usuário
        """
        return self.plan
    
    def get_plan_limits(self) -> dict:
        """
        Retorna limites do plano atual
        
        Returns:
            dict: Limites do plano
        """
        limits = {
            "free": {"agents": 0, "flows": 0, "executions": 0},
            "basic": {"agents": 5, "flows": 10, "executions": 100},
            "pro": {"agents": 50, "flows": 100, "executions": 1000},
            "enterprise": {"agents": -1, "flows": -1, "executions": -1}
        }
        return limits.get(self.plan, limits["free"])
