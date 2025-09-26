"""
API de arquivos para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Dict, Any, Optional

from models.file_models import FileResponse, FileUpdate
from models.user_models import UserResponse
from services.file_service import FileService
from itvalleysecurity.fastapi import require_access
from dependencies.service_providers import get_file_service

router = APIRouter()

@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Faz upload de um arquivo
    
    Args:
        file: Arquivo a ser enviado
        description: Descrição do arquivo
        tags: Tags para categorização
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do arquivo enviado
        
    Raises:
        HTTPException: Se arquivo inválido ou erro no upload
    """
    
    
    try:
        uploaded_file = await file_service.upload_file(
            user_id=user_token["sub"],
            file=file,
            description=description,
            tags=tags or []
        )
        
        return uploaded_file
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no upload: {str(e)}"
        )

@router.get("/", response_model=List[FileResponse])
async def get_user_files(
    file_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Busca arquivos do usuário
    
    Args:
        file_type: Tipo de arquivo para filtrar
        tags: Tags para filtrar
        limit: Limite de arquivos
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de arquivos
    """
    
    
    files = file_service.get_user_files(
        user_id=user_token["sub"],
        file_type=file_type,
        tags=tags,
        limit=limit
    )
    
    return files

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Busca arquivo por ID
    
    Args:
        file_id: ID do arquivo
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do arquivo
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    file_data = file_service.get_file(file_id, user_token["sub"])
    
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    return file_data

@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    metadata: FileUpdate,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Atualiza metadados do arquivo
    
    Args:
        file_id: ID do arquivo
        metadata: Novos metadados
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Dados do arquivo atualizado
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    try:
        updated_file = file_service.update_file(
            file_id=file_id,
            user_id=user_token["sub"],
            metadata=metadata
        )
        
        return updated_file
        
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

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Deleta um arquivo
    
    Args:
        file_id: ID do arquivo
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    success = file_service.delete_file(file_id, user_token["sub"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    return {"message": "Arquivo deletado com sucesso"}

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Faz download de um arquivo
    
    Args:
        file_id: ID do arquivo
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Arquivo para download
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    try:
        file_data = file_service.download_file(file_id, user_token["sub"])
        
        return file_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no download: {str(e)}"
        )

@router.post("/{file_id}/share")
async def share_file(
    file_id: int,
    share_with: List[str],
    permissions: str = "read",
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Compartilha um arquivo com outros usuários
    
    Args:
        file_id: ID do arquivo
        share_with: Lista de emails dos usuários
        permissions: Permissões (read, write, admin)
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Status do compartilhamento
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    try:
        share_result = file_service.share_file(
            file_id=file_id,
            user_id=user_token["sub"],
            share_with=share_with,
            permissions=permissions
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

@router.get("/{file_id}/shared")
async def get_shared_users(
    file_id: int,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Retorna lista de usuários com quem o arquivo foi compartilhado
    
    Args:
        file_id: ID do arquivo
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de usuários compartilhados
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    shared_users = file_service.get_shared_users(file_id, user_token["sub"])
    
    if shared_users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    return shared_users

@router.post("/{file_id}/process")
async def process_file(
    file_id: int,
    process_type: str,
    options: Optional[Dict[str, Any]] = None,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Processa um arquivo (OCR, análise, conversão, etc.)
    
    Args:
        file_id: ID do arquivo
        process_type: Tipo de processamento
        options: Opções de processamento
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Status do processamento
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    try:
        process_result = await file_service.process_file(
            file_id=file_id,
            user_id=user_token["sub"],
            process_type=process_type,
            options=options or {}
        )
        
        return process_result
        
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

@router.get("/{file_id}/content")
async def get_file_content(
    file_id: int,
    format: str = "text",
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Retorna conteúdo processado do arquivo
    
    Args:
        file_id: ID do arquivo
        format: Formato do conteúdo (text, json, html)
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Conteúdo do arquivo
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    try:
        content = file_service.get_file_content(
            file_id=file_id,
            user_id=user_token["sub"],
            format=format
        )
        
        return content
        
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

@router.post("/{file_id}/analyze")
async def analyze_file(
    file_id: int,
    analysis_type: str,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Analisa um arquivo usando IA
    
    Args:
        file_id: ID do arquivo
        analysis_type: Tipo de análise
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Resultado da análise
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    
    
    try:
        analysis_result = await file_service.analyze_file(
            file_id=file_id,
            user_id=user_token["sub"],
            analysis_type=analysis_type
        )
        
        return analysis_result
        
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

@router.get("/search")
async def search_files(
    query: str,
    file_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20,
    user_token = Depends(require_access),
    file_service: FileService = Depends(get_file_service)
):
    """
    Busca arquivos por texto, tipo ou tags
    
    Args:
        query: Texto para busca
        file_type: Tipo de arquivo para filtrar
        tags: Tags para filtrar
        limit: Limite de resultados
        user_token: Token do usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Lista de arquivos encontrados
    """
    
    
    search_results = file_service.search_files(
        user_id=user_token["sub"],
        query=query,
        file_type=file_type,
        tags=tags,
        limit=limit
    )
    
    return {
        "query": query,
        "results": search_results,
        "total": len(search_results)
    }

