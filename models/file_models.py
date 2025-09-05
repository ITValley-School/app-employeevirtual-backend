"""
Modelos de dados para arquivos e documentos do sistema EmployeeVirtual
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Enum as SQLEnum, ForeignKey, text
from sqlalchemy.sql import func
from data.base import Base
from models.uuid_models import UUIDColumn


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

# Modelos SQLAlchemy (para banco de dados)
class File(Base):
    """Tabela de arquivos"""
    __tablename__ = "files"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    agent_id = Column(UUIDColumn, ForeignKey('empl.agents.id'), nullable=True, index=True)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    file_size = Column(Integer, nullable=False)
    orion_file_id = Column(String(100), nullable=True)
    status = Column(SQLEnum(FileStatus), default=FileStatus.UPLOADED, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<File(id={self.id}, name='{self.original_name}', type='{self.file_type}')>"

class FileProcessing(Base):
    """Tabela de processamentos de arquivos"""
    __tablename__ = "file_processing"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    file_id = Column(UUIDColumn, ForeignKey('empl.files.id'), nullable=False, index=True)
    processing_type = Column(SQLEnum(ProcessingType), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    result = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    orion_task_id = Column(String(100), nullable=True)
    config = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FileProcessing(id={self.id}, file_id={self.file_id}, type='{self.processing_type}')>"

class OrionService(Base):
    """Tabela de serviços do Orion"""
    __tablename__ = "orion_services"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    service_type = Column(String(50), nullable=False)
    file_id = Column(UUIDColumn, ForeignKey('empl.files.id'), nullable=True, index=True)
    agent_id = Column(UUIDColumn, ForeignKey('empl.agents.id'), nullable=True, index=True)
    status = Column(String(50), default="pending", nullable=False)
    request_data = Column(Text, nullable=True)  # JSON string
    response_data = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    orion_task_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<OrionService(id={self.id}, type='{self.service_type}', status='{self.status}')>"

class DataLakeFile(Base):
    """Tabela de arquivos no Data Lake"""
    __tablename__ = "datalake_files"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    file_id = Column(UUIDColumn, ForeignKey('empl.files.id'), nullable=False, index=True)
    datalake_path = Column(String(500), nullable=False)
    datalake_url = Column(String(500), nullable=False)
    file_metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DataLakeFile(id={self.id}, file_id={self.file_id}, path='{self.datalake_path}')>"

