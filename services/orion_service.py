"""
Serviço de integração com Orion (serviços de IA) para o sistema EmployeeVirtual
"""
import httpx
import json
import base64
from typing import Optional, Dict, Any
from datetime import datetime


class OrionService:
    """Serviço para integração com Orion (serviços de IA)"""
    
    def __init__(self, base_url: str = "https://orion-api.example.com"):
        self.base_url = base_url
        self.client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Obtém cliente HTTP reutilizável"""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient()
        return self.client
    
    async def call_service(self, service_type: str, file_url: Optional[str] = None, 
                          file_content: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Chama serviço do Orion
        
        Args:
            service_type: Tipo de serviço (transcription, ocr, analysis, etc.)
            file_url: URL do arquivo
            file_content: Conteúdo do arquivo em base64
            parameters: Parâmetros específicos do serviço
            
        Returns:
            Resultado do serviço
        """
        session = await self._get_session()
        
        endpoint_map = {
            "transcription": "/api/transcription",
            "youtube_transcription": "/api/youtube-transcription",
            "ocr": "/api/ocr",
            "pdf_analysis": "/api/pdf-analysis",
            "document_analysis": "/api/document-analysis",
            "image_analysis": "/api/image-analysis",
            "video_analysis": "/api/video-analysis"
        }
        
        endpoint = endpoint_map.get(service_type)
        if not endpoint:
            return {
                "status": "error",
                "error_message": f"Serviço não suportado: {service_type}"
            }
        
        url = f"{self.base_url}{endpoint}"
        
        payload = {
            "service_type": service_type,
            "parameters": parameters or {}
        }
        
        if file_url:
            payload["file_url"] = file_url
        elif file_content:
            payload["file_content"] = file_content
        else:
            return {
                "status": "error",
                "error_message": "file_url ou file_content é obrigatório"
            }
        
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "success",
                        "result": result,
                        "orion_task_id": result.get("task_id"),
                        "processing_time": result.get("processing_time")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "error_message": f"Erro HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Erro na chamada do Orion: {str(e)}"
            }
    
    async def transcribe_audio(self, file_url: str, language: str = "pt-BR") -> Dict[str, Any]:
        """
        Transcreve áudio
        
        Args:
            file_url: URL do arquivo de áudio
            language: Idioma da transcrição
            
        Returns:
            Resultado da transcrição
        """
        return await self.call_service(
            service_type="transcription",
            file_url=file_url,
            parameters={"language": language}
        )
    
    async def transcribe_youtube(self, youtube_url: str, language: str = "pt-BR") -> Dict[str, Any]:
        """
        Transcreve vídeo do YouTube
        
        Args:
            youtube_url: URL do vídeo do YouTube
            language: Idioma da transcrição
            
        Returns:
            Resultado da transcrição
        """
        return await self.call_service(
            service_type="youtube_transcription",
            parameters={"youtube_url": youtube_url, "language": language}
        )
    
    async def extract_text_from_image(self, file_url: str) -> Dict[str, Any]:
        """
        Extrai texto de imagem (OCR)
        
        Args:
            file_url: URL da imagem
            
        Returns:
            Texto extraído
        """
        return await self.call_service(
            service_type="ocr",
            file_url=file_url
        )
    
    async def analyze_pdf(self, file_url: str, analysis_type: str = "full") -> Dict[str, Any]:
        """
        Analisa documento PDF
        
        Args:
            file_url: URL do PDF
            analysis_type: Tipo de análise (full, summary, extract)
            
        Returns:
            Resultado da análise
        """
        return await self.call_service(
            service_type="pdf_analysis",
            file_url=file_url,
            parameters={"analysis_type": analysis_type}
        )
    
    async def upload_to_datalake(self, file_content: bytes, file_name: str, 
                                user_id: int, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Faz upload de arquivo para o Data Lake
        
        Args:
            file_content: Conteúdo do arquivo
            file_name: Nome do arquivo
            user_id: ID do usuário
            metadata: Metadados do arquivo
            
        Returns:
            Informações do upload
        """
        session = await self._get_session()
        
        # Codificar arquivo em base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "file_name": file_name,
            "file_content": file_base64,
            "user_id": user_id,
            "metadata": metadata or {},
            "upload_timestamp": datetime.utcnow().isoformat()
        }
        
        url = f"{self.base_url}/api/datalake/upload"
        
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "success",
                        "file_id": result.get("file_id"),
                        "datalake_url": result.get("datalake_url"),
                        "datalake_path": result.get("datalake_path")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "error_message": f"Erro no upload: HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Erro no upload para Data Lake: {str(e)}"
            }
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Verifica status de uma tarefa no Orion
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Status da tarefa
        """
        session = await self._get_session()
        
        url = f"{self.base_url}/api/tasks/{task_id}/status"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "success",
                        "task_status": result.get("status"),
                        "progress": result.get("progress"),
                        "result": result.get("result"),
                        "error_message": result.get("error_message")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "error_message": f"Erro ao verificar status: HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Erro ao verificar status da tarefa: {str(e)}"
            }
    
    async def vectorize_document(self, file_url: str, chunk_size: int = 1000, 
                                overlap: int = 200) -> Dict[str, Any]:
        """
        Vetoriza documento para RAG
        
        Args:
            file_url: URL do documento
            chunk_size: Tamanho dos chunks
            overlap: Sobreposição entre chunks
            
        Returns:
            IDs dos vetores criados
        """
        return await self.call_service(
            service_type="document_analysis",
            file_url=file_url,
            parameters={
                "action": "vectorize",
                "chunk_size": chunk_size,
                "overlap": overlap
            }
        )
    
    async def search_vectors(self, query: str, vector_ids: list, top_k: int = 5) -> Dict[str, Any]:
        """
        Busca semântica nos vetores
        
        Args:
            query: Query de busca
            vector_ids: IDs dos vetores para buscar
            top_k: Número de resultados
            
        Returns:
            Resultados da busca
        """
        session = await self._get_session()
        
        payload = {
            "query": query,
            "vector_ids": vector_ids,
            "top_k": top_k
        }
        
        url = f"{self.base_url}/api/vectors/search"
        
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "status": "success",
                        "results": result.get("results", [])
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "error_message": f"Erro na busca: HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Erro na busca semântica: {str(e)}"
            }
    
    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()

