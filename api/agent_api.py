"""
API de agentes para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from models.agent_models import AgentCreate, AgentUpdate, AgentResponse, AgentExecutionRequest
from models.user_models import UserResponse
from services.agent_service import AgentService
from api.auth_api import get_current_user_dependency
from data.database import get_db

router = APIRouter()

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Cria um novo agente personalizado
    
    Args:
        agent_data: Dados do agente
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do agente criado
    """
    agent_service = AgentService(db)
    
    try:
        agent = agent_service.create_agent(current_user.id, agent_data)
        return agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[AgentResponse])
async def get_user_agents(
    include_system: bool = True,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca agentes do usuário
    
    Args:
        include_system: Incluir agentes do sistema
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de agentes
    """
    agent_service = AgentService(db)
    
    agents = agent_service.get_user_agents(current_user.id, include_system)
    
    return agents

@router.get("/system")
async def get_system_agents(db: Session = Depends(get_db)):
    """
    Busca agentes do sistema (públicos)
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Lista de agentes do sistema
    """
    agent_service = AgentService(db)
    
    system_agents = agent_service.get_system_agents()
    
    return {
        "agents": system_agents,
        "total": len(system_agents)
    }

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca agente por ID
    
    Args:
        agent_id: ID do agente
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do agente
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    agent_service = AgentService(db)
    
    agent = agent_service.get_agent_by_id(agent_id, current_user.id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Atualiza agente
    
    Args:
        agent_id: ID do agente
        agent_data: Dados a serem atualizados
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do agente atualizado
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    agent_service = AgentService(db)
    
    agent = agent_service.update_agent(agent_id, current_user.id, agent_data)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return agent

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Deleta agente
    
    Args:
        agent_id: ID do agente
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    agent_service = AgentService(db)
    
    success = agent_service.delete_agent(agent_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return {"message": "Agente deletado com sucesso"}

@router.post("/{agent_id}/execute")
async def execute_agent(
    agent_id: int,
    execution_data: AgentExecutionRequest,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Executa um agente
    
    Args:
        agent_id: ID do agente
        execution_data: Dados da execução
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resultado da execução
        
    Raises:
        HTTPException: Se agente não encontrado ou erro na execução
    """
    agent_service = AgentService(db)
    
    try:
        result = await agent_service.execute_agent(
            agent_id=agent_id,
            user_id=current_user.id,
            user_message=execution_data.user_message,
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
            detail=f"Erro na execução do agente: {str(e)}"
        )

@router.get("/{agent_id}/executions")
async def get_agent_executions(
    agent_id: int,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca execuções do agente
    
    Args:
        agent_id: ID do agente
        limit: Limite de execuções
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de execuções
    """
    agent_service = AgentService(db)
    
    executions = agent_service.get_agent_executions(agent_id, current_user.id, limit)
    
    return {
        "executions": executions,
        "total": len(executions)
    }

@router.post("/{agent_id}/knowledge")
async def add_knowledge_to_agent(
    agent_id: int,
    file_data: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Adiciona conhecimento ao agente
    
    Args:
        agent_id: ID do agente
        file_data: Dados do arquivo
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do conhecimento adicionado
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    agent_service = AgentService(db)
    
    try:
        knowledge = agent_service.add_knowledge_to_agent(
            agent_id=agent_id,
            user_id=current_user.id,
            file_data=file_data
        )
        
        return knowledge
        
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

@router.get("/{agent_id}/knowledge")
async def get_agent_knowledge(
    agent_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca base de conhecimento do agente
    
    Args:
        agent_id: ID do agente
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de arquivos de conhecimento
    """
    # Verificar se agente existe e pertence ao usuário
    agent_service = AgentService(db)
    agent = agent_service.get_agent_by_id(agent_id, current_user.id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    # Buscar conhecimento (implementar query direta)
    from models.agent_models import AgentKnowledge
    knowledge_files = db.query(AgentKnowledge).filter(
        AgentKnowledge.agent_id == agent_id
    ).all()
    
    return {
        "knowledge_files": [
            {
                "id": k.id,
                "file_name": k.file_name,
                "file_type": k.file_type,
                "file_size": k.file_size,
                "processed": k.processed,
                "created_at": k.created_at,
                "processed_at": k.processed_at
            }
            for k in knowledge_files
        ],
        "total": len(knowledge_files)
    }

@router.post("/chat")
async def quick_chat(
    agent_id: int,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Chat rápido com agente (sem salvar conversação)
    
    Args:
        agent_id: ID do agente
        message: Mensagem do usuário
        context: Contexto adicional
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resposta do agente
    """
    agent_service = AgentService(db)
    
    try:
        result = await agent_service.execute_agent(
            agent_id=agent_id,
            user_id=current_user.id,
            user_message=message,
            context=context or {}
        )
        
        return {
            "agent_response": result["response"],
            "execution_time": result.get("execution_time"),
            "model_used": result.get("model_used"),
            "success": result.get("success")
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no chat: {str(e)}"
        )

