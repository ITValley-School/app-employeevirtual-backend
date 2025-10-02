"""
Entidade de flow - Coração do domínio
Seguindo padrão IT Valley Architecture
"""
from dataclasses import dataclass
from typing import Any, Optional, List, Dict
from datetime import datetime
from uuid import uuid4


@dataclass
class FlowEntity:
    """
    Entidade de flow - Coração do domínio
    Contém apenas dados e comportamentos essenciais
    """
    id: str
    name: str
    description: Optional[str]
    type: str
    status: str = "active"
    steps: List[Dict[str, Any]] = None
    triggers: List[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    user_id: str = ""
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.steps is None:
            self.steps = []
        if self.triggers is None:
            self.triggers = []
    
    def activate(self) -> None:
        """Ativa o flow"""
        if self.status == "error":
            raise ValueError("Flow com erro não pode ser ativado")
        self.status = "active"
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Desativa o flow"""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()
    
    def start_execution(self) -> None:
        """Inicia execução do flow"""
        if self.status != "active":
            raise ValueError("Apenas flows ativos podem ser executados")
        self.status = "running"
        self.updated_at = datetime.utcnow()
    
    def finish_execution(self, success: bool = True) -> None:
        """Finaliza execução do flow"""
        if self.status != "running":
            raise ValueError("Flow não está em execução")
        
        self.status = "active" if success else "error"
        self.updated_at = datetime.utcnow()
    
    def add_step(self, step: Dict[str, Any]) -> None:
        """Adiciona passo ao flow"""
        if not self.steps:
            self.steps = []
        self.steps.append(step)
        self.updated_at = datetime.utcnow()
    
    def add_trigger(self, trigger: Dict[str, Any]) -> None:
        """Adiciona trigger ao flow"""
        if not self.triggers:
            self.triggers = []
        self.triggers.append(trigger)
        self.updated_at = datetime.utcnow()
    
    def apply_update_from_any(self, data: Any) -> None:
        """Aplica atualizações de qualquer fonte de dados"""
        def _get(data: Any, key: str, default=None):
            if hasattr(data, key):
                return getattr(data, key)
            elif isinstance(data, dict):
                return data.get(key, default)
            return default
        
        new_name = _get(data, "name")
        if new_name and len(new_name.strip()) >= 2:
            self.name = new_name.strip()
        
        new_description = _get(data, "description")
        if new_description is not None:
            self.description = new_description.strip() if new_description else None
        
        new_type = _get(data, "type")
        if new_type:
            self.type = new_type
        
        new_status = _get(data, "status")
        if new_status:
            self.status = new_status
        
        new_steps = _get(data, "steps")
        if new_steps:
            self.steps = new_steps
        
        new_triggers = _get(data, "triggers")
        if new_triggers:
            self.triggers = new_triggers
        
        new_settings = _get(data, "settings")
        if new_settings:
            self.settings = new_settings
        
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Verifica se flow está ativo"""
        return self.status == "active"
    
    def is_running(self) -> bool:
        """Verifica se flow está em execução"""
        return self.status == "running"
    
    def can_execute(self) -> bool:
        """Verifica se flow pode ser executado"""
        return self.is_active() and len(self.steps) > 0
    
    def get_execution_config(self) -> Dict[str, Any]:
        """Retorna configuração de execução"""
        return {
            "steps": self.steps,
            "triggers": self.triggers,
            "settings": self.settings or {}
        }
    
    def validate_configuration(self) -> List[str]:
        """Valida configuração do flow"""
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
        
        if not self.steps or len(self.steps) == 0:
            errors.append("Flow deve ter pelo menos um passo")
        
        if not self.triggers or len(self.triggers) == 0:
            errors.append("Flow deve ter pelo menos um trigger")
        
        return errors
