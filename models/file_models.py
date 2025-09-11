"""
Modelos de domínio para arquivos e documentos do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    """Tipos de arquivo suportados"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    PPTX = "pptx"
    PPT = "ppt"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"

class FileStatus(str, Enum):
    """Status do arquivo"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    DELETED = "deleted"

class ProcessingType(str, Enum):
    """Tipos de processamento"""
    OCR = "ocr"
    TRANSCRIPTION = "transcription"
    VECTORIZATION = "vectorization"
    ANALYSIS = "analysis"

# Modelos Pydantic (para API)
class FileBase(BaseModel):
    """Modelo base do arquivo"""
    original_name: str = Field(..., description="Nome original do arquivo")
    file_type: FileType = Field(..., description="Tipo do arquivo")
    file_size: int = Field(..., ge=0, description="Tamanho do arquivo em bytes")
    
class FileUploadRequest(BaseModel):
    """Solicitação de upload de arquivo"""
    agent_id: Optional[int] = Field(None, description="ID do agente (para base de conhecimento)")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do arquivo")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags do arquivo")
    auto_process: bool = Field(default=True, description="Processar automaticamente")
    
class FileResponse(FileBase):
    """Modelo de resposta do arquivo"""
    id: int
    user_id: int
    agent_id: Optional[int] = None
    file_path: str
    file_url: str
    orion_file_id: Optional[str] = None
    status: FileStatus
    description: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FileProcessingRequest(BaseModel):
    """Solicitação de processamento de arquivo"""
    file_id: int = Field(..., description="ID do arquivo")
    processing_type: ProcessingType = Field(..., description="Tipo de processamento")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configurações do processamento")
    
class FileProcessingResponse(BaseModel):
    """Resposta do processamento"""
    file_id: int
    processing_type: ProcessingType
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime
    
class OrionServiceRequest(BaseModel):
    """Solicitação para serviços do Orion"""
    service_type: str = Field(..., description="Tipo de serviço (transcription, ocr, analysis)")
    file_url: Optional[str] = Field(None, description="URL do arquivo")
    file_content: Optional[str] = Field(None, description="Conteúdo do arquivo em base64")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parâmetros específicos")
    
class OrionServiceResponse(BaseModel):
    """Resposta dos serviços do Orion"""
    service_type: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    orion_task_id: Optional[str] = None

class FileUpdate(BaseModel):
    """Modelo para atualização de arquivo"""
    description: Optional[str] = Field(None, max_length=500, description="Descrição do arquivo")
    tags: Optional[List[str]] = Field(None, description="Tags do arquivo")
    
    class Config:
        from_attributes = True

