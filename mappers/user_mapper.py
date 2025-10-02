"""
Mapper para usuários
Converte entre Entity (domínio) e Response (API)
Seguindo padrão IT Valley Architecture
"""
from typing import Optional
from datetime import datetime

from schemas.users.responses import (
    UserResponse, 
    UserDetailResponse, 
    UserListResponse,
    UserStatsResponse
)
from data.entities.user_entities import UserEntity


class UserMapper:
    """Mapper para conversão de usuários"""
    
    @staticmethod
    def to_public(user: UserEntity) -> UserResponse:
        """
        Converte UserEntity para UserResponse (visão pública)
        
        Args:
            user: Entidade do domínio
            
        Returns:
            UserResponse: Dados públicos do usuário
        """
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            plan=user.plan,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
    
    @staticmethod
    def to_detail(user: UserEntity, stats: Optional[dict] = None) -> UserDetailResponse:
        """
        Converte UserEntity para UserDetailResponse (visão detalhada)
        
        Args:
            user: Entidade do domínio
            stats: Estatísticas opcionais do usuário
            
        Returns:
            UserDetailResponse: Dados detalhados do usuário
        """
        return UserDetailResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            plan=user.plan,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            total_agents=stats.get('total_agents', 0) if stats else 0,
            total_flows=stats.get('total_flows', 0) if stats else 0,
            total_executions=stats.get('total_executions', 0) if stats else 0
        )
    
    @staticmethod
    def to_list(users: list[UserEntity], total: int, page: int, size: int) -> UserListResponse:
        """
        Converte lista de UserEntity para UserListResponse
        
        Args:
            users: Lista de entidades do domínio
            total: Total de usuários
            page: Página atual
            size: Tamanho da página
            
        Returns:
            UserListResponse: Lista formatada para API
        """
        return UserListResponse(
            users=[UserMapper.to_public(user) for user in users],
            total=total,
            page=page,
            size=size
        )
    
    @staticmethod
    def to_stats(user: UserEntity, stats: dict) -> UserStatsResponse:
        """
        Converte UserEntity para UserStatsResponse (estatísticas)
        
        Args:
            user: Entidade do domínio
            stats: Estatísticas do usuário
            
        Returns:
            UserStatsResponse: Estatísticas formatadas
        """
        return UserStatsResponse(
            user_id=user.id,
            total_agents=stats.get('total_agents', 0),
            total_flows=stats.get('total_flows', 0),
            total_executions=stats.get('total_executions', 0),
            last_activity=stats.get('last_activity')
        )
    
    @staticmethod
    def to_display(user: UserEntity) -> dict:
        """
        Converte UserEntity para formato de exibição simples
        
        Args:
            user: Entidade do domínio
            
        Returns:
            dict: Dados para exibição (nome e cargo apenas)
        """
        return {
            "id": user.id,
            "name": user.name,
            "plan": user.plan
        }
