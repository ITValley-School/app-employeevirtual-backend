"""
Serviço de arquivos para o sistema EmployeeVirtual - Nova implementação limpa
Usa apenas repositories para acesso a dados
"""
import os
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, BinaryIO, Union
from sqlalchemy.orm import Session

from data.file_repository import FileRepository
from data.user_repository import UserRepository
from models.file_models import (
    FileUploadRequest, FileUpdate, FileResponse, FileType, FileStatus,
    FileProcessingRequest, FileProcessingResponse, OrionServiceRequest, OrionServiceResponse
)


class FileService:
    """Serviço para gerenciamento de arquivos - Nova implementação"""
    
    def __init__(self, db: Session, storage_path: str = "./uploads"):
        self.file_repository = FileRepository(db)
        self.user_repository = UserRepository(db)
        self.storage_path = storage_path
        
        # Criar diretório de storage se não existir
        os.makedirs(storage_path, exist_ok=True)
    
    def upload_file(self, user_id: int, agent_id: Optional[int], original_name: str, 
                   file_type: FileType, file_size: int, file_content: BinaryIO,
                   description: Optional[str] = None, tags: Optional[List[str]] = None) -> FileResponse:
        """
        Faz upload de um arquivo
        
        Args:
            user_id: ID do usuário
            agent_id: ID do agente (opcional)
            original_name: Nome original do arquivo
            file_type: Tipo do arquivo
            file_size: Tamanho do arquivo
            file_content: Conteúdo binário do arquivo
            description: Descrição do arquivo
            tags: Tags do arquivo
            
        Returns:
            FileResponse: Dados do arquivo criado
        """
        # Verificar limite de storage do usuário
        current_usage = self.file_repository.get_total_file_size(user_id)
        storage_limit = self._get_user_storage_limit(user_id)
        
        if current_usage + file_size > storage_limit:
            raise ValueError("Limite de armazenamento excedido")
        
        # Gerar nome único para o arquivo
        file_extension = os.path.splitext(original_name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.storage_path, unique_filename)
        
        # Gerar URL do arquivo (assumindo configuração de servidor)
        file_url = f"/files/{unique_filename}"
        
        # Salvar arquivo no sistema de arquivos
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content.read())
        except Exception as e:
            raise ValueError(f"Erro ao salvar arquivo: {str(e)}")
        
        # Criar registro no banco
        db_file = self.file_repository.create_file(
            user_id=user_id,
            agent_id=agent_id,
            original_name=original_name,
            file_path=file_path,
            file_url=file_url,
            file_type=file_type,
            file_size=file_size,
            description=description,
            tags=tags
        )
        
        # Registrar atividade se possível
        try:
            if hasattr(self.user_repository, 'create_activity'):
                self.user_repository.create_activity(
                    user_id=user_id,
                    activity_type="file_uploaded",
                    description=f"Arquivo '{original_name}' enviado"
                )
        except Exception:
            # Se não conseguir registrar atividade, continua
            pass
        
        return self._convert_to_response(db_file)
    
    def get_file_by_id(self, file_id: int, user_id: int) -> Optional[FileResponse]:
        """
        Busca arquivo por ID
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            
        Returns:
            FileResponse ou None se não encontrado
        """
        db_file = self.file_repository.get_file_by_id(file_id, user_id)
        if not db_file:
            return None
        
        return self._convert_to_response(db_file)
    
    def get_user_files(self, user_id: int, skip: int = 0, limit: int = 50,
                      file_type: Optional[FileType] = None, search: Optional[str] = None,
                      agent_id: Optional[int] = None, status: Optional[FileStatus] = None) -> List[FileResponse]:
        """
        Busca arquivos do usuário
        
        Args:
            user_id: ID do usuário
            skip: Offset para paginação
            limit: Limite de resultados
            file_type: Tipo específico de arquivo
            search: Texto para busca
            agent_id: ID do agente
            status: Status do arquivo
            
        Returns:
            Lista de arquivos
        """
        files = self.file_repository.get_user_files(
            user_id, skip, limit, file_type, search, agent_id, status
        )
        
        return [self._convert_to_response(file) for file in files]
    
    def update_file(self, file_id: int, user_id: int, description: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> Optional[FileResponse]:
        """
        Atualiza dados do arquivo
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            description: Nova descrição
            tags: Novas tags
            
        Returns:
            FileResponse ou None se não encontrado
        """
        # Preparar dados para atualização
        update_data = {}
        if description is not None:
            update_data['description'] = description
        if tags is not None:
            update_data['tags'] = tags
        
        db_file = self.file_repository.update_file(file_id, user_id, **update_data)
        if not db_file:
            return None
        
        return self._convert_to_response(db_file)
    
    def delete_file(self, file_id: int, user_id: int) -> bool:
        """
        Remove um arquivo
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            
        Returns:
            bool: True se removido com sucesso
        """
        # Buscar arquivo primeiro para validar
        db_file = self.file_repository.get_file_by_id(file_id, user_id)
        if not db_file:
            return False
        
        # Remover arquivo físico se existir
        try:
            if os.path.exists(db_file.file_path):
                os.remove(db_file.file_path)
        except Exception:
            # Se não conseguir remover o arquivo físico, continua
            pass
        
        # Remover do banco
        success = self.file_repository.delete_file(file_id, user_id)
        
        if success:
            # Registrar atividade
            try:
                if hasattr(self.user_repository, 'create_activity'):
                    self.user_repository.create_activity(
                        user_id=user_id,
                        activity_type="file_deleted",
                        description=f"Arquivo '{db_file.original_name}' removido"
                    )
            except Exception:
                pass
        
        return success
    
    # Métodos para Tags
    def add_file_tags(self, file_id: int, user_id: int, tags: List[str]) -> Optional[FileResponse]:
        """
        Adiciona tags a um arquivo
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            tags: Lista de tags para adicionar
            
        Returns:
            FileResponse ou None se arquivo não encontrado
        """
        db_file = self.file_repository.add_file_tags(file_id, user_id, tags)
        if not db_file:
            return None
        
        return self._convert_to_response(db_file)
    
    def remove_file_tags(self, file_id: int, user_id: int, tags: List[str]) -> Optional[FileResponse]:
        """
        Remove tags de um arquivo
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            tags: Lista de tags para remover
            
        Returns:
            FileResponse ou None se arquivo não encontrado
        """
        db_file = self.file_repository.remove_file_tags(file_id, user_id, tags)
        if not db_file:
            return None
        
        return self._convert_to_response(db_file)
    
    def get_file_tags(self, file_id: int, user_id: int) -> List[str]:
        """
        Busca tags de um arquivo
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            
        Returns:
            Lista de tags
        """
        return self.file_repository.get_file_tags(file_id, user_id)
    
    def get_files_by_tag(self, user_id: int, tag_name: str) -> List[FileResponse]:
        """
        Busca arquivos por tag
        
        Args:
            user_id: ID do usuário
            tag_name: Nome da tag
            
        Returns:
            Lista de arquivos
        """
        files = self.file_repository.get_files_by_tag(user_id, tag_name)
        return [self._convert_to_response(file) for file in files]
    
    def get_popular_tags(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Busca tags mais utilizadas pelo usuário
        
        Args:
            user_id: ID do usuário
            limit: Limite de resultados
            
        Returns:
            Lista de tags com contagem
        """
        return self.file_repository.get_popular_tags(user_id, limit)
    
    # Métodos para processamento
    def create_file_processing(self, file_id: int, user_id: int, processing_type: str,
                              config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Cria um processamento de arquivo
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            processing_type: Tipo de processamento
            config: Configurações do processamento
            
        Returns:
            Dados do processamento criado
        """
        # Verificar se arquivo existe e pertence ao usuário
        db_file = self.file_repository.get_file_by_id(file_id, user_id)
        if not db_file:
            return None
        
        processing = self.file_repository.create_file_processing(
            file_id, processing_type, config
        )
        
        return {
            'id': processing.id,
            'file_id': processing.file_id,
            'processing_type': processing.processing_type,
            'status': processing.status,
            'created_at': processing.created_at
        }
    
    def get_file_processings(self, file_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Busca processamentos de um arquivo
        
        Args:
            file_id: ID do arquivo
            user_id: ID do usuário
            
        Returns:
            Lista de processamentos
        """
        # Verificar se arquivo existe e pertence ao usuário
        db_file = self.file_repository.get_file_by_id(file_id, user_id)
        if not db_file:
            return []
        
        processings = self.file_repository.get_file_processings(file_id)
        
        return [
            {
                'id': p.id,
                'file_id': p.file_id,
                'processing_type': p.processing_type,
                'status': p.status,
                'result': json.loads(p.result) if p.result else None,
                'error_message': p.error_message,
                'created_at': p.created_at,
                'completed_at': p.completed_at
            }
            for p in processings
        ]
    
    # Busca e estatísticas
    def search_files(self, user_id: int, query: str, file_type: Optional[FileType] = None,
                    tags: Optional[List[str]] = None, limit: int = 50) -> List[FileResponse]:
        """
        Busca avançada de arquivos
        
        Args:
            user_id: ID do usuário
            query: Texto para busca
            file_type: Tipo de arquivo
            tags: Tags para filtrar
            limit: Limite de resultados
            
        Returns:
            Lista de arquivos
        """
        files = self.file_repository.search_files(user_id, query, file_type, tags, limit)
        return [self._convert_to_response(file) for file in files]
    
    def get_file_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Busca estatísticas de arquivos do usuário
        
        Args:
            user_id: ID do usuário
            days: Período em dias para estatísticas
            
        Returns:
            Dicionário com estatísticas
        """
        return self.file_repository.get_file_statistics(user_id, days)
    
    def get_storage_usage(self, user_id: int) -> Dict[str, Any]:
        """
        Busca uso de storage do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com dados de uso de storage
        """
        return self.file_repository.get_storage_usage(user_id)
    
    def get_files_by_type(self, user_id: int, file_type: FileType, limit: int = 50) -> List[FileResponse]:
        """
        Busca arquivos por tipo
        
        Args:
            user_id: ID do usuário
            file_type: Tipo de arquivo
            limit: Limite de resultados
            
        Returns:
            Lista de arquivos
        """
        files = self.file_repository.get_files_by_type(user_id, file_type, limit)
        return [self._convert_to_response(file) for file in files]
    
    def get_recent_files(self, user_id: int, days: int = 7, limit: int = 20) -> List[FileResponse]:
        """
        Busca arquivos recentes
        
        Args:
            user_id: ID do usuário
            days: Número de dias
            limit: Limite de resultados
            
        Returns:
            Lista de arquivos recentes
        """
        files = self.file_repository.get_recent_files(user_id, days, limit)
        return [self._convert_to_response(file) for file in files]
    
    # Métodos privados/auxiliares
    def _convert_to_response(self, db_file) -> FileResponse:
        """
        Converte modelo SQLAlchemy para Pydantic response
        
        Args:
            db_file: Objeto File do SQLAlchemy
            
        Returns:
            FileResponse: Objeto Pydantic
        """
        # Converter tags de JSON string para lista
        tags = []
        if db_file.tags:
            try:
                tags = json.loads(db_file.tags)
            except (json.JSONDecodeError, TypeError):
                tags = []
        
        return FileResponse(
            id=db_file.id,
            user_id=db_file.user_id,
            agent_id=db_file.agent_id,
            original_name=db_file.original_name,
            file_path=db_file.file_path,
            file_url=db_file.file_url,
            file_type=db_file.file_type,
            file_size=db_file.file_size,
            orion_file_id=db_file.orion_file_id,
            status=db_file.status,
            description=db_file.description,
            tags=tags,
            created_at=db_file.created_at,
            updated_at=db_file.updated_at,
            processed_at=db_file.processed_at
        )
    
    def _get_user_storage_limit(self, user_id: int) -> int:
        """
        Obtém limite de storage do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            int: Limite em bytes
        """
        # Por enquanto retorna limite padrão de 1GB
        # Futuramente pode consultar plano do usuário
        return 1024 * 1024 * 1024  # 1GB
    
    def _get_file_type_from_extension(self, filename: str) -> FileType:
        """
        Determina tipo do arquivo baseado na extensão
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            FileType: Tipo do arquivo
        """
        extension = os.path.splitext(filename)[1].lower()
        
        type_mapping = {
            '.pdf': FileType.PDF,
            '.docx': FileType.DOCX,
            '.doc': FileType.DOC,
            '.txt': FileType.TXT,
            '.csv': FileType.CSV,
            '.xlsx': FileType.XLSX,
            '.xls': FileType.XLS,
            '.pptx': FileType.PPTX,
            '.ppt': FileType.PPT,
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.png': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.mp3': FileType.AUDIO,
            '.wav': FileType.AUDIO,
            '.mp4': FileType.VIDEO,
            '.avi': FileType.VIDEO,
        }
        
        return type_mapping.get(extension, FileType.OTHER)
