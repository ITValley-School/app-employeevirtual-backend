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
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client
    
    async def call_service(self, service_type: str, file_url: Optional[str] = None, 
                          file_content: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Chama serviço do Orion
        
        Args:
            service_type: Tipo de serviço (transcription, ocr, analysis, etc.)
            file_url: URL do arquivo a ser processado
            file_content: Conteúdo do arquivo em base64
            parameters: Parâmetros adicionais para o serviço
            
        Returns:
            Resultado do serviço
        """
        client = await self._get_client()
        
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
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "result": result,
                    "execution_time": result.get("execution_time", 0),
                    "service_type": service_type
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "error_message": f"Erro na API: {response.status_code}",
                    "error_details": error_text,
                    "service_type": service_type
                }
                
        except httpx.TimeoutException:
            return {
                "status": "error",
                "error_message": "Timeout na requisição",
                "service_type": service_type
            }
        except httpx.RequestError as e:
            return {
                "status": "error",
                "error_message": f"Erro de conexão: {str(e)}",
                "service_type": service_type
            }
        except Exception as e:
            return {
                "status": "error", 
                "error_message": f"Erro inesperado: {str(e)}",
                "service_type": service_type
            }
    
    async def transcribe_audio(self, file_url: str, language: str = "pt-BR", 
                              format_output: bool = True) -> Dict[str, Any]:
        """
        Transcreve arquivo de áudio
        
        Args:
            file_url: URL do arquivo de áudio
            language: Idioma da transcrição
            format_output: Se deve formatar a saída
            
        Returns:
            Resultado da transcrição
        """
        parameters = {
            "language": language,
            "format_output": format_output,
            "include_timestamps": True
        }
        
        return await self.call_service("transcription", file_url=file_url, parameters=parameters)
    
    async def transcribe_youtube(self, video_url: str, language: str = "pt-BR") -> Dict[str, Any]:
        """
        Transcreve vídeo do YouTube
        
        Args:
            video_url: URL do vídeo do YouTube
            language: Idioma da transcrição
            
        Returns:
            Resultado da transcrição
        """
        parameters = {
            "language": language,
            "include_metadata": True
        }
        
        return await self.call_service("youtube_transcription", file_url=video_url, parameters=parameters)
    
    async def extract_text_from_image(self, file_url: str) -> Dict[str, Any]:
        """
        Extrai texto de imagem (OCR)
        
        Args:
            file_url: URL da imagem
            
        Returns:
            Texto extraído
        """
        parameters = {
            "detect_language": True,
            "include_confidence": True
        }
        
        return await self.call_service("ocr", file_url=file_url, parameters=parameters)
    
    async def upload_and_process_file(self, file_content: bytes, filename: str, 
                                     user_id: int, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Faz upload e processa arquivo no Orion
        
        Args:
            file_content: Conteúdo do arquivo
            filename: Nome do arquivo
            user_id: ID do usuário
            metadata: Metadados do arquivo
            
        Returns:
            Resultado do upload e processamento
        """
        client = await self._get_client()
        
        # Codificar arquivo em base64
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        url = f"{self.base_url}/api/files/upload"
        
        payload = {
            "filename": filename,
            "file_content": file_b64,
            "user_id": user_id,
            "metadata": metadata or {},
            "auto_process": True
        }
        
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "result": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Erro no upload: {response.status_code}",
                    "error_details": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Erro no upload: {str(e)}"
            }
    
    async def get_processing_status(self, task_id: str) -> Dict[str, Any]:
        """
        Verifica status de processamento
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Status do processamento
        """
        client = await self._get_client()
        
        url = f"{self.base_url}/api/tasks/{task_id}/status"
        
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "result": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Erro ao consultar status: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Erro ao consultar status: {str(e)}"
            }
    
    async def analyze_document(self, file_url: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analisa documento com IA
        
        Args:
            file_url: URL do documento
            analysis_type: Tipo de análise (comprehensive, summary, entities, etc.)
            
        Returns:
            Resultado da análise
        """
        parameters = {
            "analysis_type": analysis_type,
            "extract_entities": True,
            "generate_summary": True,
            "detect_language": True
        }
        
        return await self.call_service("document_analysis", file_url=file_url, parameters=parameters)
    
    async def analyze_image(self, file_url: str, include_objects: bool = True, 
                           include_faces: bool = False) -> Dict[str, Any]:
        """
        Analisa imagem com IA
        
        Args:
            file_url: URL da imagem
            include_objects: Detectar objetos
            include_faces: Detectar faces
            
        Returns:
            Resultado da análise
        """
        client = await self._get_client()
        
        url = f"{self.base_url}/api/image-analysis"
        
        payload = {
            "file_url": file_url,
            "parameters": {
                "include_objects": include_objects,
                "include_faces": include_faces,
                "include_text": True,
                "confidence_threshold": 0.7
            }
        }
        
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "result": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error_message": f"Erro na análise: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Erro na análise: {str(e)}"
            }
    
    async def close(self):
        """Fecha cliente HTTP"""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
    
    def get_available_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna lista de serviços disponíveis
        
        Returns:
            Dicionário com serviços e suas descrições
        """
        return {
            "transcription": {
                "name": "Transcrição de Áudio",
                "description": "Transcreve arquivos de áudio para texto",
                "formats": ["mp3", "wav", "m4a", "flac"],
                "parameters": ["language", "format_output", "include_timestamps"]
            },
            "youtube_transcription": {
                "name": "Transcrição YouTube",
                "description": "Transcreve vídeos do YouTube",
                "formats": ["youtube_url"],
                "parameters": ["language", "include_metadata"]
            },
            "ocr": {
                "name": "OCR (Reconhecimento de Texto)",
                "description": "Extrai texto de imagens e documentos",
                "formats": ["png", "jpg", "jpeg", "pdf"],
                "parameters": ["detect_language", "include_confidence"]
            },
            "pdf_analysis": {
                "name": "Análise de PDF",
                "description": "Análise completa de documentos PDF",
                "formats": ["pdf"],
                "parameters": ["extract_tables", "extract_images", "analyze_structure"]
            },
            "document_analysis": {
                "name": "Análise de Documentos",
                "description": "Análise inteligente de documentos",
                "formats": ["pdf", "docx", "txt"],
                "parameters": ["analysis_type", "extract_entities", "generate_summary"]
            },
            "image_analysis": {
                "name": "Análise de Imagens",
                "description": "Análise de conteúdo visual",
                "formats": ["png", "jpg", "jpeg"],
                "parameters": ["include_objects", "include_faces", "include_text"]
            },
            "video_analysis": {
                "name": "Análise de Vídeos",
                "description": "Análise de conteúdo de vídeo",
                "formats": ["mp4", "avi", "mov"],
                "parameters": ["extract_frames", "analyze_audio", "include_timestamps"]
            }
        }
