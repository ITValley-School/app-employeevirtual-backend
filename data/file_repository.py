"""
Repositório de arquivos para o sistema EmployeeVirtual
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_

from data.entities import FileEntity, FileProcessingEntity, DataLakeFileEntity, OrionServiceEntity
from models.file_models import FileStatus, FileType


class FileRepository:
    """Repositório para operações de dados de arquivos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # CRUD Arquivos principais
    def create_file(self, user_id: int, agent_id: Optional[int], original_name: str, 
                   file_path: str, file_url: str, file_type: FileType, file_size: int,
                   orion_file_id: Optional[str] = None, description: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> FileEntity:
        """Cria um novo registro de arquivo"""
        db_file = FileEntity(
            user_id=user_id,
            agent_id=agent_id,
            original_name=original_name,
            file_path=file_path,
            file_url=file_url,
            file_type=file_type,
            file_size=file_size,
            orion_file_id=orion_file_id,
            status=FileStatus.UPLOADED,
            description=description,
            tags=json.dumps(tags or [])
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file
    
    def get_file_by_id(self, file_id: int, user_id: Optional[int] = None) -> Optional[FileEntity]:
        """Busca arquivo por ID"""
        query = self.db.query(FileEntity).filter(FileEntity.id == file_id)
        if user_id:
            query = query.filter(FileEntity.user_id == user_id)
        return query.first()
    
    def get_file_by_path(self, file_path: str, user_id: int) -> Optional[FileEntity]:
        """Busca arquivo por caminho"""
        return self.db.query(FileEntity).filter(
            and_(
                FileEntity.file_path == file_path,
                FileEntity.user_id == user_id
            )
        ).first()
    
    def get_user_files(self, user_id: int, skip: int = 0, limit: int = 50,
                      file_type: Optional[FileType] = None, search: Optional[str] = None,
                      agent_id: Optional[int] = None, status: Optional[FileStatus] = None) -> List[FileEntity]:
        """Busca arquivos do usuário"""
        query = self.db.query(FileEntity).filter(FileEntity.user_id == user_id)
        
        if file_type:
            query = query.filter(FileEntity.file_type == file_type)
        
        if agent_id:
            query = query.filter(FileEntity.agent_id == agent_id)
            
        if status:
            query = query.filter(FileEntity.status == status)
        
        if search:
            query = query.filter(
                or_(
                    FileEntity.original_name.ilike(f"%{search}%"),
                    FileEntity.description.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(desc(FileEntity.created_at)).offset(skip).limit(limit).all()
    
    def get_files_by_type(self, user_id: int, file_type: FileType, limit: int = 50) -> List[FileEntity]:
        """Busca arquivos por tipo"""
        return self.db.query(FileEntity).filter(
            and_(
                FileEntity.user_id == user_id,
                FileEntity.file_type == file_type
            )
        ).order_by(desc(FileEntity.created_at)).limit(limit).all()
    
    def get_recent_files(self, user_id: int, days: int = 7, limit: int = 20) -> List[FileEntity]:
        """Busca arquivos recentes"""
        since_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(FileEntity).filter(
            and_(
                FileEntity.user_id == user_id,
                FileEntity.created_at >= since_date
            )
        ).order_by(desc(FileEntity.created_at)).limit(limit).all()
    
    def update_file(self, file_id: int, user_id: int, **kwargs) -> Optional[FileEntity]:
        """Atualiza dados do arquivo"""
        file_obj = self.get_file_by_id(file_id, user_id)
        if not file_obj:
            return None
        
        for key, value in kwargs.items():
            if hasattr(file_obj, key) and value is not None:
                if key == 'tags' and isinstance(value, list):
                    setattr(file_obj, key, json.dumps(value))
                else:
                    setattr(file_obj, key, value)
        
        file_obj.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(file_obj)
        return file_obj
    
    def delete_file(self, file_id: int, user_id: int) -> bool:
        """Remove arquivo"""
        file_obj = self.get_file_by_id(file_id, user_id)
        if not file_obj:
            return False
        
        # Remover processamentos relacionados
        self.db.query(FileProcessingEntity).filter(FileProcessingEntity.file_id == file_id).delete()
        
        # Remover serviços Orion relacionados
        self.db.query(OrionServiceEntity).filter(OrionServiceEntity.file_id == file_id).delete()
        
        # Remover registros do DataLake relacionados
        self.db.query(DataLakeFileEntity).filter(DataLakeFileEntity.file_id == file_id).delete()
        
        # Remover arquivo
        self.db.delete(file_obj)
        self.db.commit()
        return True
    
    def get_files_count(self, user_id: int, file_type: Optional[FileType] = None, 
                       status: Optional[FileStatus] = None) -> int:
        """Retorna contagem de arquivos"""
        query = self.db.query(FileEntity).filter(FileEntity.user_id == user_id)
        if file_type:
            query = query.filter(FileEntity.file_type == file_type)
        if status:
            query = query.filter(FileEntity.status == status)
        return query.count()
    
    def get_total_file_size(self, user_id: int) -> int:
        """Retorna tamanho total dos arquivos do usuário"""
        result = self.db.query(func.sum(FileEntity.file_size)).filter(
            FileEntity.user_id == user_id
        ).scalar()
        return result or 0
    
    # Métodos para Tags (armazenadas como JSON no campo tags)
    def add_file_tags(self, file_id: int, user_id: int, new_tags: List[str]) -> Optional[FileEntity]:
        """Adiciona tags a um arquivo"""
        file_obj = self.get_file_by_id(file_id, user_id)
        if not file_obj:
            return None
        
        # Obter tags existentes
        existing_tags = json.loads(file_obj.tags) if file_obj.tags else []
        
        # Adicionar novas tags (sem duplicatas)
        all_tags = list(set(existing_tags + new_tags))
        
        # Atualizar arquivo
        file_obj.tags = json.dumps(all_tags)
        file_obj.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(file_obj)
        return file_obj
    
    def remove_file_tags(self, file_id: int, user_id: int, tags_to_remove: List[str]) -> Optional[FileEntity]:
        """Remove tags de um arquivo"""
        file_obj = self.get_file_by_id(file_id, user_id)
        if not file_obj:
            return None
        
        # Obter tags existentes
        existing_tags = json.loads(file_obj.tags) if file_obj.tags else []
        
        # Remover tags especificadas
        updated_tags = [tag for tag in existing_tags if tag not in tags_to_remove]
        
        # Atualizar arquivo
        file_obj.tags = json.dumps(updated_tags)
        file_obj.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(file_obj)
        return file_obj
    
    def get_file_tags(self, file_id: int, user_id: int) -> List[str]:
        """Busca tags de um arquivo"""
        file_obj = self.get_file_by_id(file_id, user_id)
        if not file_obj or not file_obj.tags:
            return []
        
        try:
            return json.loads(file_obj.tags)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_files_by_tag(self, user_id: int, tag_name: str) -> List[FileEntity]:
        """Busca arquivos por tag"""
        files = self.db.query(FileEntity).filter(FileEntity.user_id == user_id).all()
        
        matching_files = []
        for FileEntity in files:
            if FileEntity.tags:
                try:
                    tags = json.loads(FileEntity.tags)
                    if tag_name in tags:
                        matching_files.append(FileEntity)
                except (json.JSONDecodeError, TypeError):
                    continue
        
        return sorted(matching_files, key=lambda x: x.created_at, reverse=True)
    
    def get_popular_tags(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca tags mais utilizadas pelo usuário"""
        files = self.db.query(FileEntity).filter(
            and_(FileEntity.user_id == user_id, FileEntity.tags.isnot(None))
        ).all()
        
        tag_counts = {}
        for FileEntity in files:
            if FileEntity.tags:
                try:
                    tags = json.loads(FileEntity.tags)
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Ordenar por contagem e retornar top N
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{'tag_name': tag, 'count': count} for tag, count in sorted_tags]
    
    # CRUD FileProcessingEntity
    def create_file_processing(self, file_id: int, processing_type: str, 
                              config: Optional[Dict[str, Any]] = None, 
                              orion_task_id: Optional[str] = None) -> FileProcessingEntity:
        """Cria um novo processamento de arquivo"""
        db_processing = FileProcessingEntity(
            file_id=file_id,
            processing_type=processing_type,
            status="pending",
            config=json.dumps(config or {}),
            orion_task_id=orion_task_id
        )
        self.db.add(db_processing)
        self.db.commit()
        self.db.refresh(db_processing)
        return db_processing
    
    def get_file_processing(self, processing_id: int) -> Optional[FileProcessingEntity]:
        """Busca processamento por ID"""
        return self.db.query(FileProcessingEntity).filter(FileProcessingEntity.id == processing_id).first()
    
    def get_file_processings(self, file_id: int) -> List[FileProcessingEntity]:
        """Busca todos os processamentos de um arquivo"""
        return self.db.query(FileProcessingEntity).filter(
            FileProcessingEntity.file_id == file_id
        ).order_by(desc(FileProcessingEntity.created_at)).all()
    
    def update_file_processing(self, processing_id: int, **kwargs) -> Optional[FileProcessingEntity]:
        """Atualiza processamento"""
        processing = self.get_file_processing(processing_id)
        if not processing:
            return None
        
        for key, value in kwargs.items():
            if hasattr(processing, key) and value is not None:
                if key == 'result' and isinstance(value, dict):
                    setattr(processing, key, json.dumps(value))
                else:
                    setattr(processing, key, value)
        
        if kwargs.get('status') in ['completed', 'error']:
            processing.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(processing)
        return processing
    
    # CRUD DataLakeFileEntity
    def create_datalake_file(self, user_id: int, file_id: int, datalake_path: str,
                           datalake_url: str, file_metadata: Optional[Dict[str, Any]] = None) -> DataLakeFileEntity:
        """Cria registro no DataLake"""
        db_datalake = DataLakeFileEntity(
            user_id=user_id,
            file_id=file_id,
            datalake_path=datalake_path,
            datalake_url=datalake_url,
            file_metadata=json.dumps(file_metadata or {})
        )
        self.db.add(db_datalake)
        self.db.commit()
        self.db.refresh(db_datalake)
        return db_datalake
    
    def get_datalake_file(self, file_id: int) -> Optional[DataLakeFileEntity]:
        """Busca arquivo no DataLake"""
        return self.db.query(DataLakeFileEntity).filter(DataLakeFileEntity.file_id == file_id).first()
    
    # CRUD OrionServiceEntity
    def create_orion_service(self, user_id: int, service_type: str, 
                           file_id: Optional[int] = None, agent_id: Optional[int] = None,
                           request_data: Optional[Dict[str, Any]] = None,
                           orion_task_id: Optional[str] = None) -> OrionServiceEntity:
        """Cria registro de serviço Orion"""
        db_orion = OrionServiceEntity(
            user_id=user_id,
            service_type=service_type,
            file_id=file_id,
            agent_id=agent_id,
            status="pending",
            request_data=json.dumps(request_data or {}),
            orion_task_id=orion_task_id
        )
        self.db.add(db_orion)
        self.db.commit()
        self.db.refresh(db_orion)
        return db_orion
    
    def get_orion_service(self, service_id: int) -> Optional[OrionServiceEntity]:
        """Busca serviço Orion por ID"""
        return self.db.query(OrionServiceEntity).filter(OrionServiceEntity.id == service_id).first()
    
    def update_orion_service(self, service_id: int, **kwargs) -> Optional[OrionServiceEntity]:
        """Atualiza serviço Orion"""
        service = self.get_orion_service(service_id)
        if not service:
            return None
        
        for key, value in kwargs.items():
            if hasattr(service, key) and value is not None:
                if key in ['request_data', 'response_data'] and isinstance(value, dict):
                    setattr(service, key, json.dumps(value))
                else:
                    setattr(service, key, value)
        
        if kwargs.get('status') in ['completed', 'error']:
            service.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(service)
        return service
    
    # Estatísticas e relatórios
    def get_file_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Busca estatísticas de arquivos"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Contagem total
        total_files = self.get_files_count(user_id)
        
        # Arquivos novos no período
        new_files = self.db.query(FileEntity).filter(
            and_(
                FileEntity.user_id == user_id,
                FileEntity.created_at >= since_date
            )
        ).count()
        
        # Tamanho total
        total_size = self.get_total_file_size(user_id)
        
        # Distribuição por tipo
        file_types = self.db.query(
            FileEntity.file_type,
            func.count(FileEntity.id).label('count'),
            func.sum(FileEntity.file_size).label('total_size')
        ).filter(FileEntity.user_id == user_id).group_by(FileEntity.file_type).all()
        
        type_distribution = [
            {
                'file_type': ft.file_type.value,
                'count': ft.count,
                'total_size': ft.total_size or 0
            }
            for ft in file_types
        ]
        
        # Distribuição por status
        status_distribution = self.db.query(
            FileEntity.status,
            func.count(FileEntity.id).label('count')
        ).filter(FileEntity.user_id == user_id).group_by(FileEntity.status).all()
        
        status_dist = [
            {
                'status': st.status.value,
                'count': st.count
            }
            for st in status_distribution
        ]
        
        return {
            'total_files': total_files,
            'new_files_period': new_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'type_distribution': type_distribution,
            'status_distribution': status_dist
        }
    
    def get_storage_usage(self, user_id: int) -> Dict[str, Any]:
        """Busca uso de storage do usuário"""
        total_size = self.get_total_file_size(user_id)
        file_count = self.get_files_count(user_id)
        
        # Assumindo limite de 1GB para usuários free (pode vir de configuração)
        storage_limit = 1024 * 1024 * 1024  # 1GB em bytes
        usage_percentage = (total_size / storage_limit) * 100 if storage_limit > 0 else 0
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_size_gb': round(total_size / (1024 * 1024 * 1024), 3),
            'file_count': file_count,
            'storage_limit_bytes': storage_limit,
            'storage_limit_gb': round(storage_limit / (1024 * 1024 * 1024), 1),
            'usage_percentage': round(usage_percentage, 2),
            'available_bytes': max(0, storage_limit - total_size),
            'available_gb': round(max(0, storage_limit - total_size) / (1024 * 1024 * 1024), 3)
        }
    
    def search_files(self, user_id: int, query: str, file_type: Optional[FileType] = None, 
                    tags: Optional[List[str]] = None, limit: int = 50) -> List[FileEntity]:
        """Busca avançada de arquivos"""
        db_query = self.db.query(FileEntity).filter(FileEntity.user_id == user_id)
        
        # Busca por texto
        if query:
            db_query = db_query.filter(
                or_(
                    FileEntity.original_name.ilike(f"%{query}%"),
                    FileEntity.description.ilike(f"%{query}%")
                )
            )
        
        # Filtro por tipo
        if file_type:
            db_query = db_query.filter(FileEntity.file_type == file_type)
        
        files = db_query.order_by(desc(FileEntity.updated_at)).limit(limit).all()
        
        # Filtro por tags (se especificado)
        if tags:
            filtered_files = []
            for FileEntity in files:
                if FileEntity.tags:
                    try:
                        file_tags = json.loads(FileEntity.tags)
                        if any(tag in file_tags for tag in tags):
                            filtered_files.append(FileEntity)
                    except (json.JSONDecodeError, TypeError):
                        continue
            return filtered_files
        
        return files
