"""
API de flows/automações para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from models.flow_models import FlowCreate, FlowUpdate, FlowResponse, FlowExecutionRequest
from models.user_models import UserResponse
from services.flow_service import FlowService
from auth.dependencies import get_current_user
from data.database import get_db

router = APIRouter()

@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    flow_data: FlowCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo flow/automação
    
    Args:
        flow_data: Dados do flow
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow criado
    """
    flow_service = FlowService(db)
    
    try:
        flow = flow_service.create_flow(current_user.id, flow_data)
        return flow
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[FlowResponse])
async def get_user_flows(
    include_templates: bool = True,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca flows do usuário
    
    Args:
        include_templates: Incluir templates do sistema
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de flows
    """
    flow_service = FlowService(db)
    
    flows = flow_service.get_user_flows(current_user.id, include_templates)
    
    return flows

@router.get("/templates")
async def get_flow_templates(db: Session = Depends(get_db)):
    """
    Busca templates de flows (públicos)
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Lista de templates
    """
    flow_service = FlowService(db)
    
    templates = flow_service.get_flow_templates()
    
    return {
        "templates": templates,
        "total": len(templates)
    }

@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca flow por ID
    
    Args:
        flow_id: ID do flow
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    flow = flow_service.get_flow_by_id(flow_id, current_user.id)
    
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza flow
    
    Args:
        flow_id: ID do flow
        flow_data: Dados a serem atualizados
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow atualizado
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    flow = flow_service.update_flow(flow_id, current_user.id, flow_data)
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow não encontrado"
        )
    
    return flow

@router.delete("/{flow_id}")
async def delete_flow(
    flow_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta flow
    
    Args:
        flow_id: ID do flow
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    success = flow_service.delete_flow(flow_id, current_user.id)
    
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executa um flow
    
    Args:
        flow_id: ID do flow
        execution_data: Dados da execução
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resultado da execução
        
    Raises:
        HTTPException: Se flow não encontrado ou erro na execução
    """
    flow_service = FlowService(db)
    
    try:
        result = await flow_service.execute_flow(
            flow_id=flow_id,
            user_id=current_user.id,
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

@router.post("/{flow_id}/execute-simple")
async def execute_flow_simple(
    flow_id: int,
    execution_data: FlowExecutionRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executa um flow de forma simples
    
    Args:
        flow_id: ID do flow
        execution_data: Dados da execução
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resultado da execução simplificado
    """
    flow_service = FlowService(db)
    
    try:
        result = await flow_service.execute_flow_simple(
            flow_id=flow_id,
            user_id=current_user.id,
            input_data=execution_data.input_data
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca execuções do flow
    
    Args:
        flow_id: ID do flow
        limit: Limite de execuções
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de execuções
    """
    flow_service = FlowService(db)
    
    executions = flow_service.get_flow_executions(flow_id, current_user.id, limit)
    
    return {
        "executions": executions,
        "total": len(executions)
    }

@router.post("/{flow_id}/duplicate")
async def duplicate_flow(
    flow_id: int,
    new_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duplica um flow existente
    
    Args:
        flow_id: ID do flow original
        new_name: Nome para o novo flow
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow duplicado
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    try:
        duplicated_flow = flow_service.duplicate_flow(
            flow_id=flow_id,
            user_id=current_user.id,
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exporta um flow
    
    Args:
        flow_id: ID do flow
        format: Formato de exportação (json, yaml, xml)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow exportado
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    try:
        exported_data = flow_service.export_flow(
            flow_id=flow_id,
            user_id=current_user.id,
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Importa um flow
    
    Args:
        flow_data: Dados do flow para importar
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do flow importado
        
    Raises:
        HTTPException: Se dados inválidos
    """
    flow_service = FlowService(db)
    
    try:
        imported_flow = flow_service.import_flow(
            user_id=current_user.id,
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna status atual do flow
    
    Args:
        flow_id: ID do flow
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Status do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    status_info = flow_service.get_flow_status(flow_id, current_user.id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow não encontrado"
        )
    
    return status_info

@router.post("/{flow_id}/pause")
async def pause_flow(
    flow_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pausa um flow em execução
    
    Args:
        flow_id: ID do flow
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Status atualizado do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    try:
        updated_status = flow_service.pause_flow(flow_id, current_user.id)
        
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
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume um flow pausado
    
    Args:
        flow_id: ID do flow
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Status atualizado do flow
        
    Raises:
        HTTPException: Se flow não encontrado
    """
    flow_service = FlowService(db)
    
    try:
        updated_status = flow_service.resume_flow(flow_id, current_user.id)
        
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

