# app/api/metadados_api.py
"""
API de Metadados - Endpoints para extração via PydanticAI.
"""
from fastapi import APIRouter, HTTPException, status


# Imports dos schemas
from schemas.metadata.request import MetadataPDFRequest, MetadataStringRequest
from integration.pydanticIA.payload.request import MetadataRequest

from schemas.metadata.response import  MetadadosResponse

# Import do service
from services.metadata_service import MetadataService
from integration.pydanticIA.repository.metadata_repository import PydanticAIRepository
from integration.pydanticIA.payload.response import MetadadoAIPayload


router = APIRouter(prefix="/metadados", tags=["Metadados"])


@router.post(
    "/extrair",
    response_model=MetadadoAIPayload,
    status_code=status.HTTP_200_OK,
    summary="Extrai metadados de texto",
    description="Recebe um texto e retorna metadados estruturados extraídos pela IA"
)
async def extrair_metadados_string(request: MetadataRequest):
    """
    Extrai metadados de um texto usando PydanticAI.
    
    **Fluxo:**
    1. Recebe texto (mínimo 100 caracteres)
    2. PydanticAI analisa e extrai metadados
    3. Retorna payload estruturado
    
    **Exemplo de uso:**
    ```json
    {
      "texto": "A receita da empresa no terceiro trimestre de 2024 foi de R$ 2,4 milhões..."
    }
    ```
    """
    try:
        # Chamar service PydanticAI
        #service = MetadataService()
        servicePydantic = PydanticAIRepository()
        #responseMetadata = await service.extract_metadata(request)
        responseMetadata = await servicePydantic.create_metadata(request)

        # Por enquanto, retornar o payload direto
        # Depois vamos adicionar Mapper (Payload → Entity → DTO)
        return  responseMetadata
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao extrair metadados: {str(e)}"
        )


@router.post(
    "/extrair-simples",
    status_code=status.HTTP_200_OK,
    summary="Extrai metadados (versão simplificada)",
    description="Recebe texto direto e retorna metadados"
)
async def extrair_metadados_simples(texto: str ):
    """
    Versão simplificada - recebe texto direto (query param ou body).
    
    **Útil para testes rápidos via Swagger.**
    """
    try:
        payload = await _pydantic_service.extract_metadata(texto)
        return payload
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check da API"
)
def health_check():
    """
    Verifica se a API está rodando.
    """
    return {
        "status": "ok",
        "service": "Metadados API",
        "pydantic_ai_ready": _pydantic_service is not None
    }