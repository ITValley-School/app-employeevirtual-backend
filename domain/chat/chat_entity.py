"""
Entidade de chat - Coração do domínio
Seguindo padrão IT Valley Architecture
"""
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime
from uuid import uuid4


@dataclass
class ChatEntity:
    """
    Entidade de chat - Coração do domínio
    Contém apenas dados e comportamentos essenciais
    """
    id: str
    title: Optional[str] = None
    session_id: Optional[str] = None
    user_id: str = ""
    message: Optional[str] = None
    role: str = "user"
    status: str = "active"
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialização pós-criação"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def close(self) -> None:
        """
        Fecha a sessão de chat
        """
        self.status = "closed"
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """
        Verifica se a sessão está ativa
        
        Returns:
            bool: True se ativa
        """
        return self.status == "active"
    
    def can_send_message(self) -> bool:
        """
        Verifica se pode enviar mensagem
        
        Returns:
            bool: True se pode enviar
        """
        return self.is_active()
    
    def get_id(self) -> str:
        """
        Retorna o ID da entidade
        """
        return self.id
    
    def get_user_id(self) -> str:
        """
        Retorna o ID do usuário
        """
        return self.user_id
    
    def get_status(self) -> str:
        """
        Retorna o status
        """
        return self.status
