"""
API de chat para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional

from models.chat_models import ChatResponse, ConversationResponse, ConversationCreate, MessageResponse
from models.user_models import UserResponse
from services.chat_service import ChatService
from auth.dependencies import get_current_user
from dependencies.service_providers import get_chat_service, get_agent_service

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    chat_data: ConversationCreate,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Cria uma nova conversa
    
    Args:
        chat_data: Dados da conversa
        current_user: Usuário atual
        chat_service: Serviço de chat
        
    Returns:
        Dados da conversa criada
    """
    try:
        chat_session = chat_service.create_conversation(current_user.id, chat_data)
        return chat_session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[ConversationResponse])
async def get_user_chat_sessions(
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Busca sessões de chat do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de sessões de chat
    """
    
    
    sessions = chat_service.get_user_chat_sessions(current_user.id)
    
    return sessions

@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_conversations(
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    limit: int = Query(50, description="Número máximo de conversas")
):
    """
    Lista as conversas do usuário
    
    Args:
        current_user: Usuário atual
        db: Sessão do banco de dados
        limit: Limite de conversas
        
    Returns:
        Lista de conversas
    """
    
    
    try:
        # Usar o repositório diretamente para pegar as conversações como objetos SQLAlchemy
        conversations = chat_service.chat_repository.get_user_conversations(current_user.id, skip=0, limit=limit)
        return [
            {
                "id": str(conv.id),
                "title": conv.title,
                "agent_id": str(conv.agent_id),
                "status": conv.status,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None
            }
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar conversas: {str(e)}"
        )

@router.get("/conversations/{conversation_id}/messages", response_model=List[Dict[str, Any]])
async def get_conversation_messages(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    limit: int = Query(100, description="Número máximo de mensagens")
):
    """
    Lista as mensagens de uma conversa
    
    Args:
        conversation_id: ID da conversa
        current_user: Usuário atual
        db: Sessão do banco de dados
        limit: Limite de mensagens
        
    Returns:
        Lista de mensagens
    """
    
    
    try:
        messages = chat_service.get_conversation_messages(conversation_id, current_user.id, limit=limit)
        return [
            {
                "id": str(msg.id),
                "conversation_id": str(msg.conversation_id),
                "content": msg.content,
                "message_type": msg.message_type,
                "user_id": str(msg.user_id) if msg.user_id else None,
                "agent_id": str(msg.agent_id) if msg.agent_id else None,
                "created_at": msg.created_at.isoformat(),
                "metadata": msg.message_metadata or {}
            }
            for msg in messages
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar mensagens: {str(e)}"
        )

@router.get("/{session_id}", response_model=ConversationResponse)
async def get_chat_session(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Busca sessão de chat por ID
    
    Args:
        session_id: ID da sessão
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da sessão
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    session = chat_service.get_chat_session(session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de chat não encontrada"
        )
    
    return session

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    session_id: int,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Busca mensagens de uma sessão de chat
    
    Args:
        session_id: ID da sessão
        limit: Limite de mensagens
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de mensagens
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    messages = chat_service.get_chat_messages(session_id, current_user.id, limit)
    
    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de chat não encontrada"
        )
    
    return messages

@router.post("/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: int,
    message: str,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Envia uma mensagem em uma sessão de chat
    
    Args:
        session_id: ID da sessão
        message: Conteúdo da mensagem
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da mensagem enviada
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    try:
        chat_message = chat_service.send_message(
            session_id=session_id,
            user_id=current_user.id,
            message=message
        )
        
        return chat_message
        
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

@router.post("/{session_id}/messages/ai", response_model=MessageResponse)
async def send_ai_message(
    session_id: int,
    message: str,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Envia uma mensagem e recebe resposta da IA
    
    Args:
        session_id: ID da sessão
        message: Conteúdo da mensagem
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da mensagem da IA
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    try:
        ai_message = await chat_service.send_ai_message(
            session_id=session_id,
            user_id=current_user.id,
            message=message
        )
        
        return ai_message
        
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

@router.delete("/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Deleta uma sessão de chat
    
    Args:
        session_id: ID da sessão
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    success = chat_service.delete_chat_session(session_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de chat não encontrada"
        )
    
    return {"message": "Sessão de chat deletada com sucesso"}

@router.post("/{session_id}/clear")
async def clear_chat_session(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Limpa mensagens de uma sessão de chat
    
    Args:
        session_id: ID da sessão
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    success = chat_service.clear_chat_session(session_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de chat não encontrada"
        )
    
    return {"message": "Mensagens da sessão limpas com sucesso"}

@router.post("/{session_id}/rename")
async def rename_chat_session(
    session_id: int,
    new_name: str,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Renomeia uma sessão de chat
    
    Args:
        session_id: ID da sessão
        new_name: Novo nome da sessão
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da sessão renomeada
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    try:
        renamed_session = chat_service.rename_chat_session(
            session_id=session_id,
            user_id=current_user.id,
            new_name=new_name
        )
        
        return renamed_session
        
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

@router.get("/{session_id}/export")
async def export_chat_session(
    session_id: int,
    format: str = "json",
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Exporta uma sessão de chat
    
    Args:
        session_id: ID da sessão
        format: Formato de exportação (json, txt, pdf)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados da sessão exportada
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    try:
        exported_data = chat_service.export_chat_session(
            session_id=session_id,
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

@router.post("/{session_id}/share")
async def share_chat_session(
    session_id: int,
    share_with: List[str],
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Compartilha uma sessão de chat com outros usuários
    
    Args:
        session_id: ID da sessão
        share_with: Lista de emails dos usuários
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Status do compartilhamento
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    try:
        share_result = chat_service.share_chat_session(
            session_id=session_id,
            user_id=current_user.id,
            share_with=share_with
        )
        
        return share_result
        
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

@router.get("/{session_id}/analytics")
async def get_chat_analytics(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Retorna análises de uma sessão de chat
    
    Args:
        session_id: ID da sessão
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Análises da sessão
        
    Raises:
        HTTPException: Se sessão não encontrada
    """
    
    
    analytics = chat_service.get_chat_analytics(session_id, current_user.id)
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de chat não encontrada"
        )
    
    return analytics

@router.post("/quick")
async def quick_chat(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Chat rápido sem salvar sessão
    
    Args:
        message: Mensagem do usuário
        context: Contexto adicional
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resposta da IA
    """
    
    
    try:
        response = await chat_service.quick_chat(
            user_id=current_user.id,
            message=message,
            context=context or {}
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no chat rápido: {str(e)}"
        )

@router.post("/agent", response_model=Dict[str, Any])
async def chat_with_agent(
    message: str,
    agent_id: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    agent_service = Depends(get_agent_service)
):
    """
    Chat direto com um agente específico (suporta UUIDs)
    
    Args:
        message: Mensagem do usuário
        agent_id: ID do agente (UUID)
        context: Contexto adicional
        current_user: Usuário atual
        chat_service: Serviço de chat
        agent_service: Serviço de agentes
        
    Returns:
        Resposta do agente
    """
    
    
    try:
        # Verificar se o agente existe e pertence ao usuário
        agent = agent_service.get_agent_by_id(agent_id, current_user.id)
        if not agent:
            # Tentar buscar como agente do sistema
            system_agents = agent_service.get_system_agents()
            agent_found = None
            for sys_agent in system_agents:
                if str(sys_agent.get('id')) == agent_id:
                    agent_found = sys_agent
                    break
            
            if not agent_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agente não encontrado"
                )
        
        # Obter conversation_id do contexto
        conversation_id = context.get('conversationId') if context else None
        print(f"🔍 Context recebido: {context}")
        print(f"🎯 ConversationId extraído: {conversation_id}")
        
        # Se não há conversation_id, criar uma nova conversa
        if not conversation_id:
            print("🆕 Criando nova conversa...")
            conversation_data = ConversationCreate(
                agent_id=agent_id,
                title=f"Conversa com {agent.name if agent else 'Agente'}"
            )
            conversation = chat_service.create_conversation(current_user.id, conversation_data)
            conversation_id = str(conversation.id)
            print(f"✅ Nova conversa criada: {conversation_id}")
        
        # Salvar mensagem do usuário
        user_message = chat_service.create_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=message,
            message_type="user"
        )
        print(f"✅ Mensagem do usuário salva: {user_message.id}")
        
        # Incluir conversation_id no context se estiver disponível
        execution_context = context or {}
        if conversation_id:
            execution_context['conversation_id'] = conversation_id
        
        # Executar agente
        response = await agent_service.execute_agent(
            agent_id=agent_id,
            user_id=current_user.id,
            user_message=message,
            context=execution_context
        )
        
        # Salvar resposta do agente
        agent_message = chat_service.create_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=response.get('response', ''),
            message_type="agent",
            agent_id=agent_id
        )
        print(f"✅ Mensagem do agente salva: {agent_message.id}")
        
        # Atualizar timestamp da última mensagem da conversa
        chat_service.update_conversation_timestamp(conversation_id)
        
        # Retornar resposta com informações da conversa
        return {
            **response,
            "conversation_id": conversation_id,
            "user_message_id": str(user_message.id),
            "agent_message_id": str(agent_message.id)
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar agente: {str(e)}"
        )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Remove uma conversa e todas suas mensagens
    
    Args:
        conversation_id: ID da conversa (UUID)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se conversa não encontrada
    """
    
    
    try:
        success = chat_service.delete_conversation(conversation_id, current_user.id)
        
        if success:
            return {"message": "Conversa removida com sucesso", "conversation_id": conversation_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover conversa: {str(e)}"
        )

