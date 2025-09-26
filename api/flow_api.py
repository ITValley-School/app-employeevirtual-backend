"""
API de flows/automações para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional

from models.flow_models import FlowCreate, FlowUpdate, FlowResponse, FlowExecutionRequest
from models.user_models import UserResponse
from services.flow_service import FlowService
from itvalleysecurity.fastapi import require_access
from dependencies.service_providers import get_flow_service

router = APIRouter()

@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    flow_data: FlowCreate,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Cria um novo flow/automação
    
    Args:
        flow_data: Dados do flow
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow criado
    """
    
    
    try:
        flow = flow_service.create_flow(user_token["sub"], flow_data)
        return flow
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[FlowResponse])
async def get_user_flows(
    include_templates: bool = True,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Busca flows do usuário
    
    Args:
        include_templates: Incluir templates do sistema
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de flows
    """
    
    
    flows = flow_service.get_user_flows(user_token["sub"], include_templates)
    
    return flows

@router.get("/templates")
async def get_flow_templates(flow_service: FlowService = Depends(get_flow_service)):
    """
    Busca templates de flows (públicos)
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Lista de templates
    """
    
    
    templates = flow_service.get_flow_templates()
    
    return {
        "templates": templates,
        "total": len(templates)
    }

@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: int,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Busca flow por ID
    
    Args:
        flow_id: ID do flow
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    flow = flow_service.get_flow_by_id(flow_id, user_token["sub"])
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow não encontrado"
        )
    
    return flow

@router.put("/{flow_id}", response_model=FlowResponse)
async def update_flow(
    flow_id: int,
    flow_data: FlowUpdate,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Atualiza flow
    
    Args:
        flow_id: ID do flow
        flow_data: Dados a serem atualizados
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow atualizado
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    flow = flow_service.update_flow(flow_id, user_token["sub"], flow_data)
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow não encontrado"
        )
    
    return flow

@router.delete("/{flow_id}")
async def delete_flow(
    flow_id: int,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Deleta flow
    
    Args:
        flow_id: ID do flow
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    success = flow_service.delete_flow(flow_id, user_token["sub"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow não encontrado"
        )
    
    return {"message": "Flow deletado com sucesso"}

@router.post("/{flow_id}/execute")
async def execute_flow(
    flow_id: int,
    execution_data: FlowExecutionRequest,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Executa um flow
    
    Args:
        flow_id: ID do flow
        execution_data: Dados da execução
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Resultado da execução
        
    Raises:
        HTTPException: Se flow não encontrado ou erro na execução
    """
    
    
    try:
        result = await flow_service.execute_flow(
            flow_id=flow_id,
            user_id=user_token["sub"],
            input_data=execution_data.input_data,
            context=execution_data.context
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na execução do flow: {str(e)}"
        )

 

@router.get("/{flow_id}/executions")
async def get_flow_executions(
    flow_id: int,
    limit: int = 50,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Busca execuções do flow
    
    Args:
        flow_id: ID do flow
        limit: Limite de execuções
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de execuções
    """
    
    
    executions = flow_service.get_flow_executions(flow_id, user_token["sub"], limit)
    
    return {
        "executions": executions,
        "total": len(executions)
    }

@router.post("/{flow_id}/duplicate")
async def duplicate_flow(
    flow_id: int,
    new_name: str,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Duplica um flow existente
    
    Args:
        flow_id: ID do flow original
        new_name: Nome para o novo flow
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow duplicado
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    try:
        duplicated_flow = flow_service.duplicate_flow(
            flow_id=flow_id,
            user_id=user_token["sub"],
            new_name=new_name
        )
        
        return duplicated_flow
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{flow_id}/export")
async def export_flow(
    flow_id: int,
    format: str = "json",
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Exporta um flow
    
    Args:
        flow_id: ID do flow
        format: Formato de exportação (json, yaml, xml)
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow exportado
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    try:
        exported_data = flow_service.export_flow(
            flow_id=flow_id,
            user_id=user_token["sub"],
            format=format
        )
        
        return exported_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/import")
async def import_flow(
    flow_data: Dict[str, Any],
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Importa um flow
    
    Args:
        flow_data: Dados do flow para importar
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow importado
        
    Raises:
        HTTPException: Se dados inválidos
    """
    
    
    try:
        imported_flow = flow_service.import_flow(
            user_id=user_token["sub"],
            flow_data=flow_data
        )
        
        return imported_flow
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{flow_id}/status")
async def get_flow_status(
    flow_id: int,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Retorna status atual do flow
    
    Args:
        flow_id: ID do flow
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Status do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    status_info = flow_service.get_flow_status(flow_id, user_token["sub"])
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow não encontrado"
        )
    
    return status_info

@router.post("/{flow_id}/pause")
async def pause_flow(
    flow_id: int,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Pausa um flow em execução
    
    Args:
        flow_id: ID do flow
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Status atualizado do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    try:
        updated_status = flow_service.pause_flow(flow_id, user_token["sub"])
        
        return updated_status
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{flow_id}/resume")
async def resume_flow(
    flow_id: int,
    user_token = Depends(require_access),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Resume um flow pausado
    
    Args:
        flow_id: ID do flow
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Status atualizado do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    
    
    try:
        updated_status = flow_service.resume_flow(flow_id, user_token["sub"])
        
        return updated_status
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

