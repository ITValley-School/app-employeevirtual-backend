"""
API de flows/automações para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from models.flow_models import FlowCreate, FlowUpdate, FlowResponse, FlowExecutionRequest, FlowExecutionResponse
from models.user_models import UserResponse
from services.flow_service import FlowService
from api.auth_api import get_current_user_dependency
from data.database import get_db

router = APIRouter()

@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    flow_data: FlowCreate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Cria um novo flow
    
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
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca flows do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de flows
    """
    flow_service = FlowService(db)
    
    flows = flow_service.get_user_flows(current_user.id)
    
    return flows

@router.get("/templates")
async def get_flow_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Busca templates de flows
    
    Args:
        category: Categoria dos templates
        db: Sessão do banco de dados
        
    Returns:
        Lista de templates
    """
    flow_service = FlowService(db)
    
    templates = flow_service.get_flow_templates(category)
    
    return {
        "templates": templates,
        "total": len(templates)
    }

@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
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
    current_user: UserResponse = Depends(get_current_user_dependency),
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
    current_user: UserResponse = Depends(get_current_user_dependency),
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

@router.post("/{flow_id}/execute", response_model=FlowExecutionResponse)
async def execute_flow(
    flow_id: int,
    execution_request: FlowExecutionRequest,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Executa um flow
    
    Args:
        flow_id: ID do flow
        execution_request: Dados da execução
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resultado da execução
        
    Raises:
        HTTPException: Se flow não encontrado ou erro na execução
    """
    flow_service = FlowService(db)
    
    # Atualizar flow_id no request
    execution_request.flow_id = flow_id
    
    try:
        result = await flow_service.execute_flow(
            flow_id=flow_id,
            user_id=current_user.id,
            execution_request=execution_request
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

@router.get("/{flow_id}/executions", response_model=List[FlowExecutionResponse])
async def get_flow_executions(
    flow_id: int,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user_dependency),
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
    
    return executions

@router.get("/{flow_id}/executions/{execution_id}", response_model=FlowExecutionResponse)
async def get_flow_execution(
    flow_id: int,
    execution_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca execução específica do flow
    
    Args:
        flow_id: ID do flow
        execution_id: ID da execução
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da execução
        
    Raises:
        HTTPException: Se execução não encontrada
    """
    from models.flow_models import FlowExecution
    
    # Verificar se execução existe e pertence ao usuário
    execution = db.query(FlowExecution).filter(
        FlowExecution.id == execution_id,
        FlowExecution.flow_id == flow_id,
        FlowExecution.user_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execução não encontrada"
        )
    
    flow_service = FlowService(db)
    result = flow_service._build_execution_response(execution)
    
    return result

@router.post("/{flow_id}/executions/{execution_id}/continue")
async def continue_flow_execution(
    flow_id: int,
    execution_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Continua execução pausada do flow
    
    Args:
        flow_id: ID do flow
        execution_id: ID da execução
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resultado da continuação
        
    Raises:
        HTTPException: Se execução não encontrada ou não pausada
    """
    from models.flow_models import FlowExecution, ExecutionStatus
    
    # Verificar se execução existe e está pausada
    execution = db.query(FlowExecution).filter(
        FlowExecution.id == execution_id,
        FlowExecution.flow_id == flow_id,
        FlowExecution.user_id == current_user.id,
        FlowExecution.status == ExecutionStatus.PAUSED
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execução não encontrada ou não está pausada"
        )
    
    # TODO: Implementar continuação da execução
    # Por enquanto, apenas atualizar status
    execution.status = ExecutionStatus.RUNNING
    db.commit()
    
    return {"message": "Execução continuada com sucesso"}

@router.post("/{flow_id}/executions/{execution_id}/cancel")
async def cancel_flow_execution(
    flow_id: int,
    execution_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Cancela execução do flow
    
    Args:
        flow_id: ID do flow
        execution_id: ID da execução
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se execução não encontrada
    """
    from models.flow_models import FlowExecution, ExecutionStatus
    
    # Verificar se execução existe
    execution = db.query(FlowExecution).filter(
        FlowExecution.id == execution_id,
        FlowExecution.flow_id == flow_id,
        FlowExecution.user_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execução não encontrada"
        )
    
    if execution.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Execução já finalizada"
        )
    
    # Cancelar execução
    execution.status = ExecutionStatus.CANCELLED
    execution.completed_at = db.func.now()
    db.commit()
    
    return {"message": "Execução cancelada com sucesso"}

@router.get("/{flow_id}/preview")
async def preview_flow(
    flow_id: int,
    input_data: Optional[Dict[str, Any]] = None,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Visualiza preview do flow sem executar
    
    Args:
        flow_id: ID do flow
        input_data: Dados de entrada para preview
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Preview do flow
        
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
    
    return {
        "flow": flow,
        "estimated_time": flow.estimated_time,
        "total_steps": len(flow.steps),
        "preview_data": input_data or {},
        "can_execute": flow.status == "active"
    }

