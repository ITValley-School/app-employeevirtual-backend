"""
API para Agentes do Sistema - Catálogo
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from data.database import get_db
from services.system_agent_service import CatalogService
from models.system_agent_models import (
    SystemAgentResponse, CategoryResponse, SystemAgentSummaryResponse, 
    UserSystemAgentResponse, UserCategoryWithAgentsResponse,
    CreateSystemAgentRequest, UpdateSystemAgentRequest,
    CreateCategoryRequest, UpdateCategoryRequest,
    CreateSystemAgentVersionRequest, UpdateSystemAgentVersionRequest,
    CreateSystemAgentVisibilityRequest, UpdateSystemAgentVisibilityRequest,
    AgentVersionResponse, AgentVisibilityResponse,
    UserPlan
)
from models.user_models import UserResponse
from auth.dependencies import get_current_user

# Router principal para catálogo
router = APIRouter(prefix="/system-agents", tags=["System Agents"])

# =============================================
# ENDPOINTS PARA USUÁRIOS FINAIS (CATÁLOGO)
# =============================================

@router.get("/catalog", response_model=List[UserCategoryWithAgentsResponse])
async def get_catalog(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Busca catálogo de agentes organizados por categoria para o usuário atual.
    Respeitando regras de visibilidade baseadas no plano, tenant e região.
    """
    try:
        service = CatalogService(db)
        
        # Extrair informações do usuário (assumindo que estão no objeto user)
        user_plan = UserPlan.FREE  # Você pode extrair do current_user.plan se existir
        tenant_id = getattr(current_user, 'tenant_id', None)
        region = getattr(current_user, 'region', None)
        
        return service.get_catalog_for_user(user_plan, tenant_id, region)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/catalog/{agent_id}", response_model=UserSystemAgentResponse)
async def get_agent_for_user(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Busca agente específico se visível para o usuário atual.
    """
    try:
        service = CatalogService(db)
        
        # Extrair informações do usuário
        user_plan = UserPlan.FREE  # Você pode extrair do current_user.plan se existir
        tenant_id = getattr(current_user, 'tenant_id', None)
        region = getattr(current_user, 'region', None)
        
        agent = service.get_agent_for_user(agent_id, user_plan, tenant_id, region)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agente não encontrado ou não visível para seu plano"
            )
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# =============================================
# ENDPOINTS PARA ADMIN - CATEGORIAS
# =============================================

@router.post("/admin/categories", response_model=CategoryResponse)
async def create_category(
    request: CreateCategoryRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cria nova categoria (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.create_category(
            name=request.name,
            icon=request.icon,
            description=request.description,
            order_index=request.order_index
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/admin/categories", response_model=List[CategoryResponse])
async def list_categories(
    include_inactive: bool = Query(False, description="Incluir categorias inativas"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Lista categorias (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.get_categories(include_inactive=include_inactive)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/admin/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Busca categoria por ID (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        category = service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.put("/admin/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    request: UpdateCategoryRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Atualiza categoria (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.icon is not None:
            updates['icon'] = request.icon
        if request.description is not None:
            updates['description'] = request.description
        if request.order_index is not None:
            updates['order_index'] = request.order_index
        if request.is_active is not None:
            updates['is_active'] = request.is_active
        
        category = service.update_category(category_id, **updates)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/admin/categories/{category_id}")
async def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Remove categoria (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        success = service.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        return {"message": "Categoria removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# =============================================
# ENDPOINTS PARA ADMIN - AGENTES
# =============================================

@router.post("/admin/agents", response_model=SystemAgentResponse)
async def create_agent(
    request: CreateSystemAgentRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cria novo agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.create_system_agent(
            name=request.name,
            short_description=request.short_description,
            category_id=request.category_id,
            icon=request.icon
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/admin/agents", response_model=List[SystemAgentSummaryResponse])
async def list_agents(
    category_id: Optional[UUID] = Query(None, description="Filtrar por categoria"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Lista agentes (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.get_system_agents(category_id=category_id, status=status)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/admin/agents/{agent_id}", response_model=SystemAgentResponse)
async def get_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Busca agente por ID (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        agent = service.get_system_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agente não encontrado"
            )
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.put("/admin/agents/{agent_id}", response_model=SystemAgentResponse)
async def update_agent(
    agent_id: UUID,
    request: UpdateSystemAgentRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Atualiza agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.short_description is not None:
            updates['short_description'] = request.short_description
        if request.category_id is not None:
            updates['category_id'] = request.category_id
        if request.icon is not None:
            updates['icon'] = request.icon
        if request.status is not None:
            updates['status'] = request.status
        
        agent = service.update_system_agent(agent_id, **updates)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agente não encontrado"
            )
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/admin/agents/{agent_id}")
async def delete_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Remove agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        success = service.delete_system_agent(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agente não encontrado"
            )
        return {"message": "Agente removido com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# =============================================
# ENDPOINTS PARA ADMIN - VERSÕES
# =============================================

@router.post("/admin/agents/{agent_id}/versions", response_model=AgentVersionResponse)
async def create_agent_version(
    agent_id: UUID,
    request: CreateSystemAgentVersionRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cria nova versão do agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.create_agent_version(
            system_agent_id=agent_id,
            version=request.version,
            input_schema=request.input_schema,
            output_schema=request.output_schema,
            orion_workflows=request.orion_workflows,
            is_default=request.is_default
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/admin/agents/{agent_id}/versions", response_model=List[AgentVersionResponse])
async def list_agent_versions(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Lista versões do agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.get_agent_versions(agent_id)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.put("/admin/versions/{version_id}", response_model=AgentVersionResponse)
async def update_agent_version(
    version_id: UUID,
    request: UpdateSystemAgentVersionRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Atualiza versão do agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        
        updates = {}
        if request.input_schema is not None:
            updates['input_schema_data'] = request.input_schema
        if request.output_schema is not None:
            updates['output_schema_data'] = request.output_schema
        if request.orion_workflows is not None:
            updates['orion_workflow_list'] = request.orion_workflows
        if request.is_default is not None:
            updates['is_default'] = request.is_default
        if request.status is not None:
            updates['status'] = request.status
        
        version = service.update_agent_version(version_id, **updates)
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Versão não encontrada"
            )
        return version
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/admin/versions/{version_id}")
async def delete_agent_version(
    version_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Remove versão do agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        success = service.delete_agent_version(version_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Versão não encontrada"
            )
        return {"message": "Versão removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# =============================================
# ENDPOINTS PARA ADMIN - REGRAS DE VISIBILIDADE
# =============================================

@router.post("/admin/agents/{agent_id}/visibility", response_model=AgentVisibilityResponse)
async def create_visibility_rule(
    agent_id: UUID,
    request: CreateSystemAgentVisibilityRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cria regra de visibilidade (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.create_visibility_rule(
            system_agent_id=agent_id,
            tenant_id=request.tenant_id,
            plan=request.plan,
            region=request.region,
            is_visible=request.is_visible
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/admin/agents/{agent_id}/visibility", response_model=List[AgentVisibilityResponse])
async def list_visibility_rules(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Lista regras de visibilidade do agente (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        return service.get_visibility_rules(agent_id)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.put("/admin/visibility/{rule_id}", response_model=AgentVisibilityResponse)
async def update_visibility_rule(
    rule_id: UUID,
    request: UpdateSystemAgentVisibilityRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Atualiza regra de visibilidade (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        
        updates = {}
        if request.tenant_id is not None:
            updates['tenant_id'] = request.tenant_id
        if request.plan is not None:
            updates['plan'] = request.plan
        if request.region is not None:
            updates['region'] = request.region
        if request.is_visible is not None:
            updates['is_visible'] = request.is_visible
        
        rule = service.update_visibility_rule(rule_id, **updates)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra não encontrada"
            )
        return rule
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.delete("/admin/visibility/{rule_id}")
async def delete_visibility_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Remove regra de visibilidade (ADMIN APENAS).
    """
    try:
        # TODO: Verificar se usuário é admin
        service = CatalogService(db)
        success = service.delete_visibility_rule(rule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra não encontrada"
            )
        return {"message": "Regra removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )
