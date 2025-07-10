"""
API de chat/conversação para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from models.chat_models import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationWithMessages, ConversationSummary, ChatRequest, ChatResponse
)
from models.user_models import UserResponse
from services.chat_service import ChatService
from api.auth_api import get_current_user_dependency
from data.database import get_db

router = APIRouter()

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova conversação
    
    Args:
        conversation_data: Dados da conversação
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da conversação criada
    """
    chat_service = ChatService(db)
    
    try:
        conversation = chat_service.create_conversation(current_user.id, conversation_data)
        return conversation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/conversations", response_model=List[ConversationSummary])
async def get_user_conversations(
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca conversações do usuário
    
    Args:
        limit: Limite de conversações
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de resumos de conversações
    """
    chat_service = ChatService(db)
    
    conversations = chat_service.get_user_conversations(current_user.id, limit)
    
    return conversations

@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation_with_messages(
    conversation_id: int,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca conversação com mensagens
    
    Args:
        conversation_id: ID da conversação
        limit: Limite de mensagens
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Conversação com mensagens
        
    Raises:
        HTTPException: Se conversação não encontrada
    """
    chat_service = ChatService(db)
    
    conversation = chat_service.get_conversation_with_messages(
        conversation_id, current_user.id, limit
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    return conversation

@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Atualiza conversação
    
    Args:
        conversation_id: ID da conversação
        conversation_data: Dados a serem atualizados
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da conversação atualizada
        
    Raises:
        HTTPException: Se conversação não encontrada
    """
    chat_service = ChatService(db)
    
    conversation = chat_service.update_conversation(
        conversation_id, current_user.id, conversation_data
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    return conversation

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Deleta conversação (soft delete)
    
    Args:
        conversation_id: ID da conversação
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se conversação não encontrada
    """
    chat_service = ChatService(db)
    
    success = chat_service.delete_conversation(conversation_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    return {"message": "Conversação deletada com sucesso"}

@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Envia mensagem e obtém resposta do agente
    
    Args:
        chat_request: Dados da mensagem
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resposta do chat
        
    Raises:
        HTTPException: Se agente não encontrado ou erro na execução
    """
    chat_service = ChatService(db)
    
    try:
        response = await chat_service.send_message(current_user.id, chat_request)
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no envio da mensagem: {str(e)}"
        )

@router.post("/conversations/{conversation_id}/context")
async def set_conversation_context(
    conversation_id: int,
    context_key: str,
    context_value: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Define contexto da conversação
    
    Args:
        conversation_id: ID da conversação
        context_key: Chave do contexto
        context_value: Valor do contexto
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se conversação não encontrada
    """
    chat_service = ChatService(db)
    
    success = chat_service.set_conversation_context(
        conversation_id, current_user.id, context_key, context_value
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    return {"message": "Contexto definido com sucesso"}

@router.get("/conversations/{conversation_id}/context")
async def get_conversation_context(
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca contexto da conversação
    
    Args:
        conversation_id: ID da conversação
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Contexto da conversação
    """
    chat_service = ChatService(db)
    
    context = chat_service.get_conversation_context(conversation_id, current_user.id)
    
    return {"context": context}

@router.post("/messages/{message_id}/reaction")
async def add_message_reaction(
    message_id: int,
    reaction_type: str,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Adiciona reação a uma mensagem
    
    Args:
        message_id: ID da mensagem
        reaction_type: Tipo da reação (like, dislike, helpful, etc.)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se mensagem não encontrada
    """
    chat_service = ChatService(db)
    
    success = chat_service.add_message_reaction(
        message_id, current_user.id, reaction_type
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensagem não encontrada"
        )
    
    return {"message": "Reação adicionada com sucesso"}

@router.post("/quick-chat")
async def quick_chat(
    agent_id: int,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Chat rápido sem criar conversação persistente
    
    Args:
        agent_id: ID do agente
        message: Mensagem do usuário
        context: Contexto adicional
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resposta do agente
        
    Raises:
        HTTPException: Se agente não encontrado
    """
    from services.agent_service import AgentService
    
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
            "agent_name": result["agent_name"],
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
            detail=f"Erro no chat rápido: {str(e)}"
        )

@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: int,
    format: str = "json",
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Exporta conversação em diferentes formatos
    
    Args:
        conversation_id: ID da conversação
        format: Formato de exportação (json, txt, md)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da conversação exportada
        
    Raises:
        HTTPException: Se conversação não encontrada
    """
    chat_service = ChatService(db)
    
    conversation = chat_service.get_conversation_with_messages(
        conversation_id, current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    if format == "json":
        return conversation
    elif format == "txt":
        # Converter para texto simples
        text_content = f"Conversação: {conversation.title}\n"
        text_content += f"Agente: {conversation.agent_name}\n"
        text_content += f"Data: {conversation.created_at}\n\n"
        
        for message in conversation.messages:
            sender = "Usuário" if message.message_type == "user" else conversation.agent_name
            text_content += f"{sender}: {message.content}\n\n"
        
        return {"content": text_content, "format": "text"}
    elif format == "md":
        # Converter para Markdown
        md_content = f"# {conversation.title}\n\n"
        md_content += f"**Agente:** {conversation.agent_name}  \n"
        md_content += f"**Data:** {conversation.created_at}  \n\n"
        
        for message in conversation.messages:
            sender = "**Usuário**" if message.message_type == "user" else f"**{conversation.agent_name}**"
            md_content += f"{sender}: {message.content}\n\n"
        
        return {"content": md_content, "format": "markdown"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato não suportado. Use: json, txt, md"
        )

