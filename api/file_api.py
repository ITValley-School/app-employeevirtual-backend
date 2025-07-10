"""
API de arquivos para o sistema EmployeeVirtual
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
import uuid
from datetime import datetime

from models.file_models import FileResponse, FileUpdate
from models.user_models import UserResponse
from services.orion_service import OrionService
from api.auth_api import get_current_user_dependency
from data.database import get_db

router = APIRouter()

@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    process_with_orion: bool = Form(True),
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Faz upload de arquivo
    
    Args:
        file: Arquivo a ser enviado
        description: Descrição do arquivo
        tags: Tags do arquivo (separadas por vírgula)
        process_with_orion: Se deve processar com Orion
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do arquivo enviado
    """
    from models.file_models import File as FileModel
    
    # Validar tipo de arquivo
    allowed_extensions = {'.pdf', '.txt', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.mp3', '.wav', '.mp4', '.avi'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não suportado: {file_extension}"
        )
    
    # Ler conteúdo do arquivo
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validar tamanho (100MB max)
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo muito grande. Tamanho máximo: 100MB"
        )
    
    # Gerar nome único
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    try:
        # Upload para Orion Data Lake
        orion_service = OrionService()
        upload_result = await orion_service.upload_to_datalake(
            file_content=file_content,
            file_name=unique_filename,
            user_id=current_user.id,
            metadata={
                "original_filename": file.filename,
                "description": description,
                "tags": tags,
                "uploaded_by": current_user.email
            }
        )
        
        if upload_result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro no upload: {upload_result.get('error_message')}"
            )
        
        # Salvar no banco de dados
        db_file = FileModel(
            user_id=current_user.id,
            original_filename=file.filename,
            stored_filename=unique_filename,
            file_type=file_extension[1:],  # Remove o ponto
            file_size=file_size,
            description=description,
            tags=tags,
            datalake_url=upload_result.get("datalake_url"),
            datalake_path=upload_result.get("datalake_path"),
            orion_file_id=upload_result.get("file_id")
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Processar com Orion se solicitado
        processing_result = None
        if process_with_orion and upload_result.get("datalake_url"):
            try:
                if file_extension in ['.pdf']:
                    processing_result = await orion_service.analyze_pdf(upload_result["datalake_url"])
                elif file_extension in ['.jpg', '.jpeg', '.png']:
                    processing_result = await orion_service.extract_text_from_image(upload_result["datalake_url"])
                elif file_extension in ['.mp3', '.wav']:
                    processing_result = await orion_service.transcribe_audio(upload_result["datalake_url"])
                
                if processing_result and processing_result["status"] == "success":
                    db_file.processed = True
                    db_file.processing_result = str(processing_result.get("result", {}))
                    db_file.orion_task_id = processing_result.get("orion_task_id")
                    db.commit()
                    
            except Exception as e:
                # Log erro mas não falha o upload
                print(f"Erro no processamento Orion: {str(e)}")
        
        return FileResponse(
            id=db_file.id,
            user_id=db_file.user_id,
            original_filename=db_file.original_filename,
            stored_filename=db_file.stored_filename,
            file_type=db_file.file_type,
            file_size=db_file.file_size,
            description=db_file.description,
            tags=db_file.tags.split(',') if db_file.tags else [],
            datalake_url=db_file.datalake_url,
            processed=db_file.processed,
            processing_result=processing_result.get("result") if processing_result else None,
            created_at=db_file.created_at,
            updated_at=db_file.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no upload do arquivo: {str(e)}"
        )

@router.get("/", response_model=List[FileResponse])
async def get_user_files(
    file_type: Optional[str] = None,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca arquivos do usuário
    
    Args:
        file_type: Filtrar por tipo de arquivo
        limit: Limite de arquivos
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Lista de arquivos
    """
    from models.file_models import File as FileModel
    from sqlalchemy import desc
    
    query = db.query(FileModel).filter(FileModel.user_id == current_user.id)
    
    if file_type:
        query = query.filter(FileModel.file_type == file_type)
    
    files = query.order_by(desc(FileModel.created_at)).limit(limit).all()
    
    return [
        FileResponse(
            id=f.id,
            user_id=f.user_id,
            original_filename=f.original_filename,
            stored_filename=f.stored_filename,
            file_type=f.file_type,
            file_size=f.file_size,
            description=f.description,
            tags=f.tags.split(',') if f.tags else [],
            datalake_url=f.datalake_url,
            processed=f.processed,
            processing_result=f.processing_result,
            created_at=f.created_at,
            updated_at=f.updated_at
        )
        for f in files
    ]

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Busca arquivo por ID
    
    Args:
        file_id: ID do arquivo
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do arquivo
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    from models.file_models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    return FileResponse(
        id=file.id,
        user_id=file.user_id,
        original_filename=file.original_filename,
        stored_filename=file.stored_filename,
        file_type=file.file_type,
        file_size=file.file_size,
        description=file.description,
        tags=file.tags.split(',') if file.tags else [],
        datalake_url=file.datalake_url,
        processed=file.processed,
        processing_result=file.processing_result,
        created_at=file.created_at,
        updated_at=file.updated_at
    )

@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    file_data: FileUpdate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Atualiza metadados do arquivo
    
    Args:
        file_id: ID do arquivo
        file_data: Dados a serem atualizados
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Dados do arquivo atualizado
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    from models.file_models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    # Atualizar campos fornecidos
    update_data = file_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tags" and isinstance(value, list):
            setattr(file, field, ','.join(value))
        else:
            setattr(file, field, value)
    
    file.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(file)
    
    return FileResponse(
        id=file.id,
        user_id=file.user_id,
        original_filename=file.original_filename,
        stored_filename=file.stored_filename,
        file_type=file.file_type,
        file_size=file.file_size,
        description=file.description,
        tags=file.tags.split(',') if file.tags else [],
        datalake_url=file.datalake_url,
        processed=file.processed,
        processing_result=file.processing_result,
        created_at=file.created_at,
        updated_at=file.updated_at
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Deleta arquivo
    
    Args:
        file_id: ID do arquivo
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    from models.file_models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    # TODO: Deletar do Data Lake também
    
    db.delete(file)
    db.commit()
    
    return {"message": "Arquivo deletado com sucesso"}

@router.post("/{file_id}/process")
async def process_file_with_orion(
    file_id: int,
    service_type: str = "auto",
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Processa arquivo com Orion
    
    Args:
        file_id: ID do arquivo
        service_type: Tipo de serviço (auto, ocr, transcription, analysis)
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        Resultado do processamento
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    from models.file_models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    if not file.datalake_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo não está disponível no Data Lake"
        )
    
    orion_service = OrionService()
    
    try:
        # Determinar tipo de serviço automaticamente
        if service_type == "auto":
            if file.file_type in ['pdf']:
                service_type = "pdf_analysis"
            elif file.file_type in ['jpg', 'jpeg', 'png']:
                service_type = "ocr"
            elif file.file_type in ['mp3', 'wav']:
                service_type = "transcription"
            else:
                service_type = "document_analysis"
        
        # Processar arquivo
        result = await orion_service.call_service(
            service_type=service_type,
            file_url=file.datalake_url
        )
        
        if result["status"] == "success":
            # Atualizar arquivo
            file.processed = True
            file.processing_result = str(result.get("result", {}))
            file.orion_task_id = result.get("orion_task_id")
            file.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "message": "Arquivo processado com sucesso",
                "result": result.get("result"),
                "task_id": result.get("orion_task_id")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro no processamento: {result.get('error_message')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no processamento do arquivo: {str(e)}"
        )

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Gera URL de download do arquivo
    
    Args:
        file_id: ID do arquivo
        current_user: Usuário atual
        db: Sessão do banco de dados
        
    Returns:
        URL de download
        
    Raises:
        HTTPException: Se arquivo não encontrado
    """
    from models.file_models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    if not file.datalake_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo não está disponível para download"
        )
    
    # TODO: Gerar URL assinada temporária
    return {
        "download_url": file.datalake_url,
        "filename": file.original_filename,
        "expires_in": 3600  # 1 hora
    }

