"""
Entidades SQLAlchemy para arquivos e documentos do sistema EmployeeVirtual
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Enum as SQLEnum, ForeignKey, text
from sqlalchemy.sql import func

from models.uuid_models import UUIDColumn
from data.base import Base
from models.file_models import FileType, FileStatus, ProcessingType


class FileEntity(Base):
    """Entidade de arquivos"""
    __tablename__ = "files"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    agent_id = Column(UUIDColumn, ForeignKey('empl.agents.id'), nullable=True, index=True)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(SQLEnum(FileStatus), default=FileStatus.UPLOADED, nullable=False)
    content_hash = Column(String(64), nullable=True, index=True)  # SHA-256
    extracted_text = Column(Text, nullable=True)
    file_metadata = Column(Text, nullable=True)  # JSON string
    processing_result = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FileEntity(id={self.id}, name='{self.original_name}', status='{self.status}')>"


class FileProcessingEntity(Base):
    """Entidade de processamento de arquivos"""
    __tablename__ = "file_processing"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    file_id = Column(UUIDColumn, ForeignKey('empl.files.id'), nullable=False, index=True)
    processing_type = Column(SQLEnum(ProcessingType), nullable=False)
    status = Column(SQLEnum(FileStatus), default=FileStatus.PROCESSING, nullable=False)
    input_data = Column(Text, nullable=True)  # JSON string
    output_data = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    provider = Column(String(50), nullable=True)  # openai, azure, local, etc.
    cost = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FileProcessingEntity(id={self.id}, file_id={self.file_id}, type='{self.processing_type}')>"


class OrionServiceEntity(Base):
    """Entidade de serviços Orion"""
    __tablename__ = "orion_services"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    user_id = Column(UUIDColumn, nullable=False, index=True)
    file_id = Column(UUIDColumn, ForeignKey('empl.files.id'), nullable=True, index=True)
    service_name = Column(String(100), nullable=False)
    service_type = Column(String(50), nullable=False)  # ocr, transcription, analysis, etc.
    input_data = Column(Text, nullable=False)  # JSON string
    output_data = Column(Text, nullable=True)  # JSON string
    status = Column(SQLEnum(FileStatus), default=FileStatus.PROCESSING, nullable=False)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    provider = Column(String(50), nullable=True)
    api_endpoint = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<OrionServiceEntity(id={self.id}, service='{self.service_name}', status='{self.status}')>"


class DataLakeFileEntity(Base):
    """Entidade de arquivos no data lake"""
    __tablename__ = "data_lake_files"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(UUIDColumn, primary_key=True, server_default=text("NEWID()"), index=True)
    file_id = Column(UUIDColumn, ForeignKey('empl.files.id'), nullable=False, index=True)
    lake_path = Column(String(500), nullable=False)
    storage_type = Column(String(50), nullable=False)  # azure, s3, local, etc.
    compressed = Column(Boolean, default=False, nullable=False)
    encrypted = Column(Boolean, default=False, nullable=False)
    backup_count = Column(Integer, default=0, nullable=False)
    last_backup = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DataLakeFileEntity(id={self.id}, file_id={self.file_id}, path='{self.lake_path}')>"
