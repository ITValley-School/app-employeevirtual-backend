"""
Entidade de agente - Coração do domínio
Seguindo padrão IT Valley Architecture
"""
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime
from uuid import uuid4


@dataclass
class AgentEntity:
    """
    Entidade de agente - Coração do domínio
    Contém apenas dados e comportamentos essenciais
    """
    id: str
    name: str
    description: Optional[str]
    type: str
    status: str = "active"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    instructions: str = ""
    system_prompt: Optional[str] = None
    user_id: str = ""
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def activate(self) -> None:
        """
        Ativa o agente
        """
        if self.status == "error":
            raise ValueError("Agente com erro não pode ser ativado")
        self.status = "active"
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """
        Desativa o agente
        """
        self.status = "inactive"
        self.updated_at = datetime.utcnow()
    
    def start_training(self) -> None:
        """
        Inicia treinamento do agente
        """
        if self.status != "active":
            raise ValueError("Apenas agentes ativos podem ser treinados")
        self.status = "training"
        self.updated_at = datetime.utcnow()
    
    def finish_training(self, success: bool = True) -> None:
        """
        Finaliza treinamento do agente
        
        Args:
            success: Se o treinamento foi bem-sucedido
        """
        if self.status != "training":
            raise ValueError("Agente não está em treinamento")
        
        self.status = "active" if success else "error"
        self.updated_at = datetime.utcnow()
    
    def update_configuration(self, **kwargs) -> None:
        """
        Atualiza configuração do agente
        
        Args:
            **kwargs: Configurações para atualizar
        """
        valid_configs = ['model', 'temperature', 'max_tokens', 'system_prompt']
        
        for key, value in kwargs.items():
            if key in valid_configs:
                setattr(self, key, value)
        
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
        
        new_description = _get(data, "description")
        if new_description is not None:
            self.description = new_description.strip() if new_description else None
        
        new_instructions = _get(data, "instructions")
        if new_instructions and len(new_instructions.strip()) >= 10:
            self.instructions = new_instructions.strip()
        
        new_type = _get(data, "type")
        if new_type:
            self.type = new_type
        
        new_status = _get(data, "status")
        if new_status:
            self.status = new_status
        
        # Atualiza configurações
        model = _get(data, "model")
        if model:
            self.model = model
        
        temperature = _get(data, "temperature")
        if temperature is not None and 0.0 <= temperature <= 2.0:
            self.temperature = temperature
        
        max_tokens = _get(data, "max_tokens")
        if max_tokens is not None and 100 <= max_tokens <= 4000:
            self.max_tokens = max_tokens
        
        system_prompt = _get(data, "system_prompt")
        if system_prompt is not None:
            self.system_prompt = system_prompt.strip() if system_prompt else None
        
        # Sempre atualiza timestamp
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """
        Verifica se agente está ativo
        
        Returns:
            bool: True se ativo
        """
        return self.status == "active"
    
    def is_training(self) -> bool:
        """
        Verifica se agente está em treinamento
        
        Returns:
            bool: True se em treinamento
        """
        return self.status == "training"
    
    def can_execute(self) -> bool:
        """
        Verifica se agente pode ser executado
        
        Returns:
            bool: True se pode executar
        """
        return self.is_active() and self.instructions.strip() != ""
    
    def get_model_config(self) -> dict:
        """
        Retorna configuração do modelo
        
        Returns:
            dict: Configuração do modelo
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_prompt": self.system_prompt
        }
    
    def validate_configuration(self) -> list[str]:
        """
        Valida configuração do agente
        
        Returns:
            list[str]: Lista de erros encontrados
        """
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
        
        if not self.instructions or len(self.instructions.strip()) < 10:
            errors.append("Instruções devem ter pelo menos 10 caracteres")
        
        if self.temperature < 0.0 or self.temperature > 2.0:
            errors.append("Temperatura deve estar entre 0.0 e 2.0")
        
        if self.max_tokens < 100 or self.max_tokens > 4000:
            errors.append("Max tokens deve estar entre 100 e 4000")
        
        return errors
