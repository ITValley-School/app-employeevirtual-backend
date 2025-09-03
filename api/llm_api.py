"""
APIs para gerenciamento de chaves LLM
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from data.database import get_db
from auth.dependencies import get_current_user, require_enterprise_user
from services.llm_key_service import LLMKeyService
from models.llm_models import (
    SystemLLMKeyCreate, SystemLLMKeyUpdate, SystemLLMKeyResponse,
    UserLLMKeyCreate, UserLLMKeyUpdate, UserLLMKeyResponse,
    LLMKeyValidationRequest, LLMKeyValidationResponse,
    LLMKeyUsageStats
)
from models.user_models import User

router = APIRouter()

# ============================================================================
# APIS PARA CHAVES DO SISTEMA (ADMIN)
# ============================================================================

@router.post("/system/keys", response_model=SystemLLMKeyResponse)
async def create_system_key(
    key_data: SystemLLMKeyCreate,
    current_user: User = Depends(require_enterprise_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova chave LLM do sistema (apenas usuários enterprise)
    """
    try:
        service = LLMKeyService(db)
        key = await service.create_system_key(key_data)
        return key
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar chave do sistema: {str(e)}"
        )

@router.get("/system/keys", response_model=List[SystemLLMKeyResponse])
async def get_system_keys(
    current_user: User = Depends(require_enterprise_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as chaves LLM do sistema (apenas usuários enterprise)
    """
    try:
        service = LLMKeyService(db)
        keys = await service.get_system_keys()
        return keys
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar chaves do sistema: {str(e)}"
        )

@router.get("/system/keys/{key_id}", response_model=SystemLLMKeyResponse)
async def get_system_key(
    key_id: str,
    current_user: User = Depends(require_enterprise_user),
    db: Session = Depends(get_db)
):
    """
    Obtém uma chave LLM específica do sistema (apenas usuários enterprise)
    """
    try:
        service = LLMKeyService(db)
        key = service.repository.get_system_key_by_id(key_id)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave do sistema não encontrada"
            )
        return key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar chave do sistema: {str(e)}"
        )

@router.put("/system/keys/{key_id}", response_model=SystemLLMKeyResponse)
async def update_system_key(
    key_id: str,
    key_data: SystemLLMKeyUpdate,
    current_user: User = Depends(require_enterprise_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma chave LLM do sistema (apenas usuários enterprise)
    """
    try:
        service = LLMKeyService(db)
        key = await service.update_system_key(key_id, key_data)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave do sistema não encontrada"
            )
        return key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar chave do sistema: {str(e)}"
        )

# ============================================================================
# APIS PARA CHAVES DO USUÁRIO
# ============================================================================

@router.post("/user/keys", response_model=UserLLMKeyResponse)
async def create_user_key(
    key_data: UserLLMKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova chave LLM para o usuário atual
    """
    try:
        service = LLMKeyService(db)
        key = await service.create_user_key(current_user.id, key_data)
        return key
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar chave do usuário: {str(e)}"
        )

@router.get("/user/keys", response_model=List[UserLLMKeyResponse])
async def get_user_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as chaves LLM do usuário atual
    """
    try:
        service = LLMKeyService(db)
        keys = await service.get_user_keys(current_user.id)
        return keys
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar chaves do usuário: {str(e)}"
        )

@router.get("/user/keys/{key_id}", response_model=UserLLMKeyResponse)
async def get_user_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém uma chave LLM específica do usuário atual
    """
    try:
        service = LLMKeyService(db)
        key = await service.get_user_key_by_id(key_id, current_user.id)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave do usuário não encontrada"
            )
        return key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar chave do usuário: {str(e)}"
        )

@router.put("/user/keys/{key_id}", response_model=UserLLMKeyResponse)
async def update_user_key(
    key_id: str,
    key_data: UserLLMKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma chave LLM do usuário atual
    """
    try:
        service = LLMKeyService(db)
        key = await service.update_user_key(key_id, current_user.id, key_data)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave do usuário não encontrada"
            )
        return key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar chave do usuário: {str(e)}"
        )

@router.delete("/user/keys/{key_id}")
async def delete_user_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove uma chave LLM do usuário atual
    """
    try:
        service = LLMKeyService(db)
        success = await service.delete_user_key(key_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave do usuário não encontrada"
            )
        return {"message": "Chave removida com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover chave do usuário: {str(e)}"
        )

# ============================================================================
# APIS DE VALIDAÇÃO E ESTATÍSTICAS
# ============================================================================

@router.post("/validate", response_model=LLMKeyValidationResponse)
async def validate_api_key(
    validation_request: LLMKeyValidationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Valida uma chave API com o provedor
    """
    try:
        service = LLMKeyService(db)
        result = await service.validate_api_key(validation_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na validação: {str(e)}"
        )

@router.get("/usage/stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas de uso das chaves do usuário atual
    """
    try:
        service = LLMKeyService(db)
        stats = await service.get_usage_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

# ============================================================================
# APIS PARA PROVEDORES DISPONÍVEIS
# ============================================================================

@router.get("/providers")
async def get_available_providers():
    """
    Lista todos os provedores LLM disponíveis
    """
    from models.llm_models import LLMProvider
    
    providers = []
    for provider in LLMProvider:
        providers.append({
            "value": provider.value,
            "name": provider.value.title(),
            "description": f"Integração com {provider.value.title()}"
        })
    
    return {
        "providers": providers,
        "total": len(providers)
    }

# ============================================================================
# APIS PARA CONFIGURAÇÃO DE AGENTES
# ============================================================================

@router.get("/agents/{agent_id}/key")
async def get_agent_key_config(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém a configuração de chave de um agente específico
    """
    try:
        service = LLMKeyService(db)
        key_config = await service.get_key_for_agent(agent_id, current_user.id)
        
        if not key_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração de chave não encontrada para este agente"
            )
        
        # Retornar apenas informações seguras (sem a chave real)
        return {
            "type": key_config["type"],
            "provider": key_config["provider"],
            "key_id": key_config["key_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter configuração de chave: {str(e)}"
        )

@router.post("/agents/{agent_id}/key/validate")
async def validate_agent_key(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Valida se a chave configurada para um agente está funcionando
    """
    try:
        service = LLMKeyService(db)
        key_config = await service.get_key_for_agent(agent_id, current_user.id)
        
        if not key_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração de chave não encontrada para este agente"
            )
        
        # Validar chave com o provedor
        validation_request = LLMKeyValidationRequest(
            provider=key_config["provider"],
            api_key=key_config["api_key"]
        )
        
        result = await service.validate_api_key(validation_request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar chave do agente: {str(e)}"
        )
