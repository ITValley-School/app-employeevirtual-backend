"""
API de agentes para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional

from models.agent_models import AgentCreate, AgentUpdate, AgentResponse, AgentExecutionRequest
from models.user_models import UserResponse
from services.agent_service import AgentService
from auth.dependencies import get_current_user
from dependencies import get_agent_service

router = APIRouter()

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Cria um novo agente personalizado
    
    Args:
        agent_data: Dados do agente
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Dados do agente criado
    """
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
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Busca agentes do usuário
    
    Args:
        include_system: Incluir agentes do sistema
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Lista de agentes
    """
    agents = agent_service.get_user_agents(current_user.id, include_system)
    
    return agents

@router.get("/system")
async def get_system_agents(agent_service: AgentService = Depends(get_agent_service)):
    """
    Busca agentes do sistema (públicos)
    
    Args:
        agent_service: Serviço de agentes
        
    Returns:
        Lista de agentes do sistema
    """
    system_agents = agent_service.get_system_agents()
    
    return {
        "agents": system_agents,
        "total": len(system_agents)
    }

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Busca agente por ID
    
    Args:
        agent_id: ID do agente
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Dados do agente
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    agent = agent_service.get_agent_by_id(agent_id, current_user.id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Atualiza agente
    
    Args:
        agent_id: ID do agente
        agent_data: Dados a serem atualizados
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Dados do agente atualizado
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    agent = agent_service.update_agent(agent_id, current_user.id, agent_data)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return agent

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Deleta agente
    
    Args:
        agent_id: ID do agente
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    success = agent_service.delete_agent(agent_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return {"message": "Agente deletado com sucesso"}

@router.post("/{agent_id}/execute")
async def execute_agent(
    agent_id: str,
    execution_data: AgentExecutionRequest,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Executa um agente
    
    Args:
        agent_id: ID do agente
        execution_data: Dados da execução
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Resultado da execução
        
    Raises:
        HTTPException: Se agente não encontrado ou erro na execução
    """
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

 

@router.post("/validate")
async def validate_agent_config(
    agent_data: AgentCreate,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Valida configuração do agente antes da criação
    
    Args:
        agent_data: Dados do agente para validar
        agent_service: Serviço de agentes
        
    Returns:
        Resultado da validação
    """
    return agent_service.validate_agent_config(agent_data)

@router.get("/{agent_id}/executions")
async def get_agent_executions(
    agent_id: str,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Busca execuções do agente
    
    Args:
        agent_id: ID do agente
        limit: Limite de execuções
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Lista de execuções
    """
    executions = agent_service.get_agent_executions(agent_id, current_user.id, limit)
    
    return {
        "executions": executions,
        "total": len(executions)
    }

@router.post("/{agent_id}/knowledge")
async def add_knowledge_to_agent(
    agent_id: str,
    file_data: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Adiciona conhecimento ao agente
    
    Args:
        agent_id: ID do agente
        file_data: Dados do arquivo
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Dados do conhecimento adicionado
        
    Raises:
        HTTPException: Se agente não encontrado
    """
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
    agent_id: str,
    current_user: UserResponse = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Busca base de conhecimento do agente
    
    Args:
        agent_id: ID do agente
        current_user: Usuário atual
        agent_service: Serviço de agentes
        
    Returns:
        Lista de arquivos de conhecimento
    """
    # Verificar se agente existe e pertence ao usuário
    agent = agent_service.get_agent_by_id(agent_id, current_user.id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    # Buscar conhecimento via serviço (não mais consulta SQL direta!)
    knowledge_files = agent_service.get_agent_knowledge(agent_id, current_user.id)
    
    return {
        "knowledge_files": knowledge_files,
        "total": len(knowledge_files)
    }

 

