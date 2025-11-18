"""
API de Metadados - Implementação IT Valley
Seguindo padrão IT Valley Architecture
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from schemas.metadata.request import MetadataStringRequest as MetadataRequest
from schemas.metadata.response import MetadadosResponse as MetadataResponse
from services.metadata_service import MetadataService
from mappers.metadata_mapper import MetadataMapper
from config.database import db_config
from auth.dependencies import get_current_user
from data.entities.user_entities import UserEntity

router = APIRouter(prefix="/metadata", tags=["metadata"])


def get_metadata_service(db: Session = Depends(db_config.get_session)) -> MetadataService:
    """Dependency para MetadataService"""
    return MetadataService(db)


@router.post("/extract", response_model=MetadataResponse, status_code=status.HTTP_200_OK)
async def extract_metadata(
    request: MetadataRequest,
    metadata_service: MetadataService = Depends(get_metadata_service),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Extrai metadados de texto
    
    Args:
        request: Dados do texto para extração
        metadata_service: Serviço de metadados
        current_user: Usuário autenticado
        
    Returns:
        MetadataResponse: Metadados extraídos
    """
    # Service orquestra extração e validações
    result = metadata_service.extract_metadata(request, current_user.id)
    
    # Converte para Response via Mapper
    return MetadataMapper.to_response(result)


@router.get("/health", response_model=dict)
async def health_check():
    """
    Health check da API de metadados
    
    Returns:
        dict: Status da API
    """
    return {
        "status": "ok",
        "service": "Metadata API",
        "architecture": "IT Valley"
    }