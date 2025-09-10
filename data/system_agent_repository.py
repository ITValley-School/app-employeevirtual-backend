"""
Repositórios para Agentes do Sistema
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from models.system_agent_models import (
    SystemAgentCategory, SystemAgent, SystemAgentVersion, 
    SystemAgentVisibility, AgentStatus, UserPlan
)
import re
import unicodedata

class SystemAgentRepository:
    """Repositório para operações com agentes do sistema"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =============================================
    # MÉTODOS PARA CATEGORIES
    # =============================================
    
    def create_category(self, name: str, icon: Optional[str] = None, 
                       description: Optional[str] = None, 
                       order_index: int = 0) -> SystemAgentCategory:
        """Cria uma nova categoria"""
        
        category = SystemAgentCategory(
            name=name,
            icon=icon,
            description=description,
            order_index=order_index
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def get_category_by_id(self, category_id: UUID) -> Optional[SystemAgentCategory]:
        """Busca categoria por ID"""
        return self.db.query(SystemAgentCategory).filter(SystemAgentCategory.id == category_id).first()
    
    def get_categories_list(self, include_inactive: bool = False) -> List[SystemAgentCategory]:
        """Lista todas as categorias ativas por padrão"""
        query = self.db.query(SystemAgentCategory)
        
        if not include_inactive:
            query = query.filter(SystemAgentCategory.is_active == True)
        
        return query.order_by(SystemAgentCategory.order_index, SystemAgentCategory.name).all()
    
    def update_category(self, category_id: UUID, **updates) -> Optional[SystemAgentCategory]:
        """Atualiza categoria"""
        category = self.get_category_by_id(category_id)
        if not category:
            return None
        
        for key, value in updates.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def delete_category(self, category_id: UUID) -> bool:
        """Remove categoria (soft delete - marca como inativa)"""
        category = self.get_category_by_id(category_id)
        if not category:
            return False
        
        category.is_active = False
        self.db.commit()
        return True
    
    # =============================================
    # MÉTODOS PARA AGENTES
    # =============================================
    
    def create_system_agent(self, name: str, short_description: str, 
                           category_id: UUID, icon: Optional[str] = None) -> SystemAgent:
        """Cria um novo agente do sistema"""
        
        agent = SystemAgent(
            name=name,
            short_description=short_description,
            category_id=category_id,
            icon=icon
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def get_system_agent_by_id(self, agent_id: UUID, 
                              include_relations: bool = True) -> Optional[SystemAgent]:
        """Busca agente por ID"""
        query = self.db.query(SystemAgent)
        
        if include_relations:
            query = query.options(
                joinedload(SystemAgent.category),
                joinedload(SystemAgent.versions),
                joinedload(SystemAgent.visibility_rules)
            )
        
        return query.filter(SystemAgent.id == agent_id).first()
    
    def get_system_agents_list(self, category_id: Optional[UUID] = None,
                              status: Optional[str] = None,
                              include_relations: bool = False) -> List[SystemAgent]:
        """Lista agentes do sistema com filtros opcionais"""
        query = self.db.query(SystemAgent)
        
        if include_relations:
            query = query.options(
                joinedload(SystemAgent.category),
                joinedload(SystemAgent.versions),
                joinedload(SystemAgent.visibility_rules)
            )
        
        if category_id:
            query = query.filter(SystemAgent.category_id == category_id)
        
        if status:
            query = query.filter(SystemAgent.status == status)
        
        return query.order_by(SystemAgent.name).all()
    
    def update_system_agent(self, agent_id: UUID, **updates) -> Optional[SystemAgent]:
        """Atualiza agente"""
        agent = self.get_system_agent_by_id(agent_id, include_relations=False)
        if not agent:
            return None
        
        for key, value in updates.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def delete_system_agent(self, agent_id: UUID) -> bool:
        """Remove agente (soft delete - marca como inativo)"""
        agent = self.get_system_agent_by_id(agent_id, include_relations=False)
        if not agent:
            return False
        
        agent.status = "inactive"
        self.db.commit()
        return True
    
    # =============================================
    # MÉTODOS PARA VERSÕES
    # =============================================
    
    def create_agent_version(self, system_agent_id: UUID, version: str,
                            input_schema: Dict[str, Any], output_schema: Dict[str, Any],
                            orion_workflows: List[str], is_default: bool = False) -> SystemAgentVersion:
        """Cria nova versão do agente"""
        
        # Se esta é a versão default, remove default das outras
        if is_default:
            self.db.query(SystemAgentVersion).filter(
                SystemAgentVersion.system_agent_id == system_agent_id,
                SystemAgentVersion.is_default == True
            ).update({SystemAgentVersion.is_default: False})
        
        version_obj = SystemAgentVersion(
            system_agent_id=system_agent_id,
            version=version,
            is_default=is_default
        )
        
        # Usar properties para converter os dados
        version_obj.input_schema_data = input_schema
        version_obj.output_schema_data = output_schema
        version_obj.orion_workflow_list = orion_workflows
        
        self.db.add(version_obj)
        self.db.commit()
        self.db.refresh(version_obj)
        return version_obj
    
    def get_agent_version_by_id(self, version_id: UUID) -> Optional[SystemAgentVersion]:
        """Busca versão por ID"""
        return self.db.query(SystemAgentVersion).filter(SystemAgentVersion.id == version_id).first()
    
    def get_agent_versions(self, system_agent_id: UUID) -> List[SystemAgentVersion]:
        """Lista versões do agente"""
        return self.db.query(SystemAgentVersion).filter(
            SystemAgentVersion.system_agent_id == system_agent_id
        ).order_by(SystemAgentVersion.version.desc()).all()
    
    def get_default_agent_version(self, system_agent_id: UUID) -> Optional[SystemAgentVersion]:
        """Busca versão padrão do agente"""
        return self.db.query(SystemAgentVersion).filter(
            SystemAgentVersion.system_agent_id == system_agent_id,
            SystemAgentVersion.is_default == True
        ).first()
    
    def update_agent_version(self, version_id: UUID, **updates) -> Optional[SystemAgentVersion]:
        """Atualiza versão do agente"""
        version = self.get_agent_version_by_id(version_id)
        if not version:
            return None
        
        # Se está marcando como default, remove default das outras
        if updates.get('is_default') == True:
            self.db.query(SystemAgentVersion).filter(
                SystemAgentVersion.system_agent_id == version.system_agent_id,
                SystemAgentVersion.id != version_id
            ).update({SystemAgentVersion.is_default: False})
        
        for key, value in updates.items():
            if hasattr(version, key):
                setattr(version, key, value)
        
        self.db.commit()
        self.db.refresh(version)
        return version
    
    def delete_agent_version(self, version_id: UUID) -> bool:
        """Remove versão do agente"""
        version = self.get_agent_version_by_id(version_id)
        if not version:
            return False
        
        self.db.delete(version)
        self.db.commit()
        return True
    
    # =============================================
    # MÉTODOS PARA REGRAS DE VISIBILIDADE
    # =============================================
    
    def create_visibility_rule(self, system_agent_id: UUID, tenant_id: Optional[str] = None,
                              plan: Optional[UserPlan] = None, region: Optional[str] = None,
                              is_visible: bool = True) -> SystemAgentVisibility:
        """Cria regra de visibilidade"""
        
        rule = SystemAgentVisibility(
            system_agent_id=system_agent_id,
            tenant_id=tenant_id,
            plan=plan,
            region=region,
            is_visible=is_visible
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_visibility_rule_by_id(self, rule_id: UUID) -> Optional[SystemAgentVisibility]:
        """Busca regra por ID"""
        return self.db.query(SystemAgentVisibility).filter(SystemAgentVisibility.id == rule_id).first()
    
    def get_visibility_rules(self, system_agent_id: UUID) -> List[SystemAgentVisibility]:
        """Lista regras de visibilidade do agente"""
        return self.db.query(SystemAgentVisibility).filter(
            SystemAgentVisibility.system_agent_id == system_agent_id
        ).all()
    
    def update_visibility_rule(self, rule_id: UUID, **updates) -> Optional[SystemAgentVisibility]:
        """Atualiza regra de visibilidade"""
        rule = self.get_visibility_rule_by_id(rule_id)
        if not rule:
            return None
        
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def delete_visibility_rule(self, rule_id: UUID) -> bool:
        """Remove regra de visibilidade"""
        rule = self.get_visibility_rule_by_id(rule_id)
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        return True
    
    # =============================================
    # MÉTODOS PARA USUÁRIOS FINAIS (COM VISIBILIDADE)
    # =============================================
    
    def get_visible_agents_by_category(self, user_plan: UserPlan, tenant_id: Optional[str] = None,
                                      region: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca agentes visíveis organizados por categoria"""
        
        # Query base para agentes ativos
        agents_query = self.db.query(SystemAgent).filter(
            SystemAgent.status == "active"
        ).options(
            joinedload(SystemAgent.category),
            joinedload(SystemAgent.versions),
            joinedload(SystemAgent.visibility_rules)
        )
        
        agents = agents_query.all()
        
        # Filtrar por visibilidade
        visible_agents = []
        for agent in agents:
            if self._is_agent_visible(agent, user_plan, tenant_id, region):
                visible_agents.append(agent)
        
        # Organizar por categoria
        categories_dict = {}
        for agent in visible_agents:
            category = agent.category
            if category.id not in categories_dict:
                categories_dict[category.id] = {
                    'category': category,
                    'agents': []
                }
            categories_dict[category.id]['agents'].append(agent)
        
        # Ordenar por order_index da categoria
        result = list(categories_dict.values())
        result.sort(key=lambda x: x['category'].order_index)
        
        return result
    
    def get_agent_for_user(self, agent_id: UUID, user_plan: UserPlan,
                          tenant_id: Optional[str] = None, region: Optional[str] = None) -> Optional[SystemAgent]:
        """Busca agente específico se visível para o usuário"""
        
        agent = self.get_system_agent_by_id(agent_id, include_relations=True)
        if not agent or agent.status != "active":
            return None
        
        if not self._is_agent_visible(agent, user_plan, tenant_id, region):
            return None
        
        return agent
    
    def _is_agent_visible(self, agent: SystemAgent, user_plan: UserPlan,
                         tenant_id: Optional[str] = None, region: Optional[str] = None) -> bool:
        """Verifica se agente é visível para o usuário baseado nas regras"""
        
        # Se não há regras de visibilidade, é visível por padrão
        if not agent.visibility_rules:
            return True
        
        # Verificar cada regra
        for rule in agent.visibility_rules:
            # Se a regra marca como não visível, verificar se se aplica ao usuário
            if not rule.is_visible:
                if self._rule_applies_to_user(rule, user_plan, tenant_id, region):
                    return False
            
            # Se a regra marca como visível, verificar se se aplica ao usuário
            if rule.is_visible:
                if self._rule_applies_to_user(rule, user_plan, tenant_id, region):
                    return True
        
        # Se chegou até aqui, verificar se há regra específica que negue
        for rule in agent.visibility_rules:
            if not rule.is_visible and self._rule_applies_to_user(rule, user_plan, tenant_id, region):
                return False
        
        # Por padrão, se há regras mas nenhuma se aplica especificamente, é visível
        return True
    
    def _rule_applies_to_user(self, rule: SystemAgentVisibility, user_plan: UserPlan,
                             tenant_id: Optional[str] = None, region: Optional[str] = None) -> bool:
        """Verifica se uma regra se aplica ao usuário"""
        
        # Se a regra especifica tenant e não bate
        if rule.tenant_id and rule.tenant_id != tenant_id:
            return False
        
        # Se a regra especifica plano e não bate
        if rule.plan and rule.plan != user_plan:
            return False
        
        # Se a regra especifica região e não bate
        if rule.region and rule.region != region:
            return False
        
        return True
