"""
Services para Agentes do Sistema - Catálogo
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from sqlalchemy.orm import Session
from data.system_agent_repository import SystemAgentRepository
from models.system_agent_models import (
    SystemAgentResponse, CategoryResponse, AgentVersionResponse, AgentVisibilityResponse,
    SystemAgentSummaryResponse, UserSystemAgentResponse, UserCategoryWithAgentsResponse,
    UserPlan
)

logger = logging.getLogger(__name__)

class CatalogService:
    """Serviço para operações do catálogo de agentes"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = SystemAgentRepository(db)
    
    # =============================================
    # MÉTODOS PARA CATEGORIAS
    # =============================================
    
    def create_category(self, name: str, icon: Optional[str] = None,
                       description: Optional[str] = None, order_index: int = 0) -> CategoryResponse:
        """Cria nova categoria"""
        category = self.repository.create_category(name, icon, description, order_index)
        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            description=category.description,
            order_index=category.order_index,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    
    def get_categories(self, include_inactive: bool = False) -> List[CategoryResponse]:
        """Lista categorias"""
        categories = self.repository.get_categories_list(include_inactive)
        return [
            CategoryResponse(
                id=cat.id,
                name=cat.name,
                icon=cat.icon,
                description=cat.description,
                order_index=cat.order_index,
                is_active=cat.is_active,
                created_at=cat.created_at,
                updated_at=cat.updated_at
            ) for cat in categories
        ]
    
    def get_category_by_id(self, category_id: UUID) -> Optional[CategoryResponse]:
        """Busca categoria por ID"""
        category = self.repository.get_category_by_id(category_id)
        if not category:
            return None
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            description=category.description,
            order_index=category.order_index,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    
    def update_category(self, category_id: UUID, **updates) -> Optional[CategoryResponse]:
        """Atualiza categoria"""
        category = self.repository.update_category(category_id, **updates)
        if not category:
            return None
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            description=category.description,
            order_index=category.order_index,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    
    def delete_category(self, category_id: UUID) -> bool:
        """Remove categoria"""
        return self.repository.delete_category(category_id)
    
    # =============================================
    # MÉTODOS PARA AGENTES (ADMIN)
    # =============================================
    
    def create_system_agent(self, name: str, short_description: str,
                           category_id: UUID, icon: Optional[str] = None) -> SystemAgentResponse:
        """Cria novo agente"""
        agent = self.repository.create_system_agent(name, short_description, category_id, icon)
        
        # Recarregar com relacionamentos
        agent = self.repository.get_system_agent_by_id(agent.id, include_relations=True)
        return self._build_agent_response(agent)
    
    def get_system_agents(self, category_id: Optional[UUID] = None,
                         status: Optional[str] = None) -> List[SystemAgentSummaryResponse]:
        """Lista agentes para admin"""
        agents = self.repository.get_system_agents_list(category_id, status, include_relations=False)
        
        result = []
        for agent in agents:
            # Buscar versão default
            default_version = self.repository.get_default_agent_version(agent.id)
            
            result.append(SystemAgentSummaryResponse(
                id=agent.id,
                name=agent.name,
                short_description=agent.short_description,
                category_id=agent.category_id,
                icon=agent.icon,
                status=agent.status,
                default_version=default_version.version if default_version else None
            ))
        
        return result
    
    def get_system_agent_by_id(self, agent_id: UUID) -> Optional[SystemAgentResponse]:
        """Busca agente por ID (admin)"""
        agent = self.repository.get_system_agent_by_id(agent_id, include_relations=True)
        if not agent:
            return None
        
        return self._build_agent_response(agent)
    
    def update_system_agent(self, agent_id: UUID, **updates) -> Optional[SystemAgentResponse]:
        """Atualiza agente"""
        agent = self.repository.update_system_agent(agent_id, **updates)
        if not agent:
            return None
        
        # Recarregar com relacionamentos
        agent = self.repository.get_system_agent_by_id(agent.id, include_relations=True)
        return self._build_agent_response(agent)
    
    def delete_system_agent(self, agent_id: UUID) -> bool:
        """Remove agente"""
        return self.repository.delete_system_agent(agent_id)
    
    # =============================================
    # MÉTODOS PARA VERSÕES
    # =============================================
    
    def create_agent_version(self, system_agent_id: UUID, version: str,
                            input_schema: Dict[str, Any], output_schema: Dict[str, Any],
                            orion_workflows: List[str], is_default: bool = False) -> AgentVersionResponse:
        """Cria nova versão"""
        version_obj = self.repository.create_agent_version(
            system_agent_id, version, input_schema, output_schema, orion_workflows, is_default
        )
        
        return AgentVersionResponse(
            id=version_obj.id,
            version=version_obj.version,
            is_default=version_obj.is_default,
            status=version_obj.status,
            input_schema=version_obj.input_schema_data,
            output_schema=version_obj.output_schema_data,
            orion_workflows=version_obj.orion_workflow_list,
            created_at=version_obj.created_at,
            updated_at=version_obj.updated_at
        )
    
    def get_agent_versions(self, system_agent_id: UUID) -> List[AgentVersionResponse]:
        """Lista versões do agente"""
        versions = self.repository.get_agent_versions(system_agent_id)
        return [
            AgentVersionResponse(
                id=v.id,
                version=v.version,
                is_default=v.is_default,
                status=v.status,
                input_schema=v.input_schema_data,
                output_schema=v.output_schema_data,
                orion_workflows=v.orion_workflow_list,
                created_at=v.created_at,
                updated_at=v.updated_at
            ) for v in versions
        ]
    
    def update_agent_version(self, version_id: UUID, **updates) -> Optional[AgentVersionResponse]:
        """Atualiza versão"""
        version = self.repository.update_agent_version(version_id, **updates)
        if not version:
            return None
        
        return AgentVersionResponse(
            id=version.id,
            version=version.version,
            is_default=version.is_default,
            status=version.status,
            input_schema=version.input_schema_data,
            output_schema=version.output_schema_data,
            orion_workflows=version.orion_workflow_list,
            created_at=version.created_at,
            updated_at=version.updated_at
        )
    
    def delete_agent_version(self, version_id: UUID) -> bool:
        """Remove versão"""
        return self.repository.delete_agent_version(version_id)
    
    # =============================================
    # MÉTODOS PARA REGRAS DE VISIBILIDADE
    # =============================================
    
    def create_visibility_rule(self, system_agent_id: UUID, tenant_id: Optional[str] = None,
                              plan: Optional[UserPlan] = None, region: Optional[str] = None,
                              is_visible: bool = True) -> AgentVisibilityResponse:
        """Cria regra de visibilidade"""
        rule = self.repository.create_visibility_rule(system_agent_id, tenant_id, plan, region, is_visible)
        
        return AgentVisibilityResponse(
            id=rule.id,
            tenant_id=rule.tenant_id,
            plan=rule.plan,
            region=rule.region,
            is_visible=rule.is_visible,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
    
    def get_visibility_rules(self, system_agent_id: UUID) -> List[AgentVisibilityResponse]:
        """Lista regras de visibilidade"""
        rules = self.repository.get_visibility_rules(system_agent_id)
        return [
            AgentVisibilityResponse(
                id=r.id,
                tenant_id=r.tenant_id,
                plan=r.plan,
                region=r.region,
                is_visible=r.is_visible,
                created_at=r.created_at,
                updated_at=r.updated_at
            ) for r in rules
        ]
    
    def update_visibility_rule(self, rule_id: UUID, **updates) -> Optional[AgentVisibilityResponse]:
        """Atualiza regra de visibilidade"""
        rule = self.repository.update_visibility_rule(rule_id, **updates)
        if not rule:
            return None
        
        return AgentVisibilityResponse(
            id=rule.id,
            tenant_id=rule.tenant_id,
            plan=rule.plan,
            region=rule.region,
            is_visible=rule.is_visible,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
    
    def delete_visibility_rule(self, rule_id: UUID) -> bool:
        """Remove regra de visibilidade"""
        return self.repository.delete_visibility_rule(rule_id)
    
    # =============================================
    # MÉTODOS PARA USUÁRIOS FINAIS
    # =============================================
    
    def get_catalog_for_user(self, user_plan: UserPlan, tenant_id: Optional[str] = None,
                            region: Optional[str] = None) -> List[UserCategoryWithAgentsResponse]:
        """Busca catálogo organizado por categoria para usuário"""
        categories_data = self.repository.get_visible_agents_by_category(user_plan, tenant_id, region)
        
        result = []
        for cat_data in categories_data:
            category = cat_data['category']
            agents = cat_data['agents']
            
            user_agents = []
            for agent in agents:
                # Buscar versão default
                default_version = self.repository.get_default_agent_version(agent.id)
                if default_version:
                    user_agents.append(UserSystemAgentResponse(
                        id=agent.id,
                        name=agent.name,
                        short_description=agent.short_description,
                        category_id=agent.category_id,
                        icon=agent.icon,
                        default_version=default_version.version,
                        input_schema=default_version.input_schema_data,
                        output_schema=default_version.output_schema_data
                    ))
            
            if user_agents:  # Só incluir categoria se há agentes visíveis
                result.append(UserCategoryWithAgentsResponse(
                    id=category.id,
                    name=category.name,
                    icon=category.icon,
                    description=category.description,
                    order_index=category.order_index,
                    agents=user_agents
                ))
        
        return result
    
    def get_agent_for_user(self, agent_id: UUID, user_plan: UserPlan,
                          tenant_id: Optional[str] = None, region: Optional[str] = None) -> Optional[UserSystemAgentResponse]:
        """Busca agente específico para usuário"""
        agent = self.repository.get_agent_for_user(agent_id, user_plan, tenant_id, region)
        if not agent:
            return None
        
        # Buscar versão default
        default_version = self.repository.get_default_agent_version(agent.id)
        if not default_version:
            return None
        
        return UserSystemAgentResponse(
            id=agent.id,
            name=agent.name,
            short_description=agent.short_description,
            category_id=agent.category_id,
            icon=agent.icon,
            default_version=default_version.version,
            input_schema=default_version.input_schema_data,
            output_schema=default_version.output_schema_data
        )
    
    # =============================================
    # MÉTODOS PRIVADOS
    # =============================================
    
    def _build_agent_response(self, agent) -> SystemAgentResponse:
        """Constrói response completo do agente"""
        # Category
        category = CategoryResponse(
            id=agent.category.id,
            name=agent.category.name,
            icon=agent.category.icon,
            description=agent.category.description,
            order_index=agent.category.order_index,
            is_active=agent.category.is_active,
            created_at=agent.category.created_at,
            updated_at=agent.category.updated_at
        )
        
        # Versions
        versions = [
            AgentVersionResponse(
                id=v.id,
                version=v.version,
                is_default=v.is_default,
                status=v.status,
                input_schema=v.input_schema_data,
                output_schema=v.output_schema_data,
                orion_workflows=v.orion_workflow_list,
                created_at=v.created_at,
                updated_at=v.updated_at
            ) for v in agent.versions
        ]
        
        # Visibility rules
        visibility_rules = [
            AgentVisibilityResponse(
                id=r.id,
                tenant_id=r.tenant_id,
                plan=r.plan,
                region=r.region,
                is_visible=r.is_visible,
                created_at=r.created_at,
                updated_at=r.updated_at
            ) for r in agent.visibility_rules
        ]
        
        return SystemAgentResponse(
            id=agent.id,
            name=agent.name,
            short_description=agent.short_description,
            category_id=agent.category_id,
            icon=agent.icon,
            status=agent.status,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            category=category,
            versions=versions,
            visibility_rules=visibility_rules
        )
