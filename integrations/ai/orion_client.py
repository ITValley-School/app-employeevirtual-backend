"""
Cliente HTTP para serviços Orion (transcrição, OCR, processamento de documentos)
"""
from __future__ import annotations

import logging
from typing import Optional, Dict, Any, BinaryIO, Union
import requests
from io import BytesIO

from config.settings import settings

logger = logging.getLogger(__name__)


class OrionClient:
    """
    Cliente responsável por comunicar com serviços Orion
    (transcrição de áudio, OCR, processamento de documentos)
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 300):
        self.base_url = (base_url or settings.orion_api_url).rstrip("/")
        self.api_key = api_key or settings.orion_api_key
        self.timeout = timeout
        
        if not self.base_url:
            logger.warning("⚠️ ORION_API_URL não configurada. Funcionalidades Orion não estarão disponíveis.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers padrão para requisições JSON"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _prepare_file(self, file_data: Union[str, bytes, BinaryIO]) -> tuple:
        """
        Prepara arquivo para upload
        
        Returns:
            tuple: (file_content, filename, content_type)
        """
        if isinstance(file_data, str):
            # Se for URL, baixa o arquivo
            if file_data.startswith("http"):
                response = requests.get(file_data, timeout=60)
                response.raise_for_status()
                file_content = response.content
                filename = file_data.split("/")[-1]
                content_type = response.headers.get("Content-Type", "application/octet-stream")
            else:
                # Assume que é caminho de arquivo local
                with open(file_data, "rb") as f:
                    file_content = f.read()
                filename = file_data.split("/")[-1]
                content_type = "application/octet-stream"
        elif isinstance(file_data, bytes):
            file_content = file_data
            filename = "file.bin"
            content_type = "application/octet-stream"
        else:
            # File-like object
            file_content = file_data.read()
            filename = getattr(file_data, "filename", "file.bin")
            content_type = getattr(file_data, "content_type", "application/octet-stream")
        
        return file_content, filename, content_type
    
    def transcribe_audio(
        self,
        audio_file: Union[str, bytes, BinaryIO],
        language: Optional[str] = "pt",
        model: str = "whisper-1"
    ) -> Dict[str, Any]:
        """
        Transcreve áudio usando Whisper da OpenAI via Orion
        
        Args:
            audio_file: Arquivo de áudio (URL, bytes ou file-like object)
            language: Código do idioma (pt, en, es, etc.) - não usado na API, mantido para compatibilidade
            model: Modelo Whisper a usar - não usado na API, mantido para compatibilidade
            
        Returns:
            Dict com transcrição e metadados
            Formato: {"transcription": "texto transcrito..."}
        """
        if not self.base_url:
            raise ValueError("Orion API URL não configurada")
        
        # Rota correta do Orion: POST /api/openai/whisper
        endpoint = f"{self.base_url}/api/openai/whisper"
        
        file_content, filename, content_type = self._prepare_file(audio_file)
        
        files = {
            "file": (filename, file_content, content_type)
        }
        
        # Orion não precisa de data adicional, apenas o arquivo
        # A API Key do Orion deve ser a OpenAI API Key
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"🎤 Transcrevendo áudio via Whisper: {filename}")
        
        response = requests.post(
            endpoint,
            files=files,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        # Orion retorna {"transcription": "texto..."}
        transcription = result.get("transcription", "")
        logger.info(f"✅ Transcrição concluída: {len(transcription)} caracteres")
        return result
    
    def transcribe_youtube(
        self,
        youtube_url: str,
        language: Optional[str] = "pt"
    ) -> Dict[str, Any]:
        """
        Transcreve vídeo do YouTube via Orion
        
        Args:
            youtube_url: URL do vídeo do YouTube
            language: Código do idioma (pt, en, etc.) - opcional
            
        Returns:
            Dict com transcrição e metadados
            Formato: {
                "success": true,
                "url": "...",
                "transcription": "texto transcrito...",
                "method": "direct" ou "whisper",
                "language": "pt"
            }
        """
        if not self.base_url:
            raise ValueError("Orion API URL não configurada")
        
        # Rota correta do Orion: POST /api/youtube/transcription
        endpoint = f"{self.base_url}/api/youtube/transcription"
        
        payload = {
            "url": youtube_url
        }
        
        # Adiciona language apenas se fornecido
        if language:
            payload["language"] = language
        
        logger.info(f"📺 Transcrevendo YouTube: {youtube_url} (idioma: {language})")
        
        # Para YouTube, não precisa de Authorization header (ou pode ser opcional)
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        # Orion retorna {"transcription": "texto..."} ou {"transcription": "..."}
        transcription = result.get("transcription", "")
        method = result.get("method", "unknown")
        logger.info(f"✅ Transcrição YouTube concluída (método: {method}): {len(transcription)} caracteres")
        return result
    
    def ocr_image(
        self,
        image_file: Union[str, bytes, BinaryIO],
        language: Optional[str] = "en"
    ) -> Dict[str, Any]:
        """
        Extrai texto de imagem usando OCR via Orion
        
        Args:
            image_file: Arquivo de imagem (URL, bytes ou file-like object)
            language: Idioma para OCR (padrão: "en", suporta: pt, en, es, etc.)
            
        Returns:
            Dict com texto extraído e metadados
            Formato: {
                "success": true,
                "extracted_text": "Texto extraído...",
                "file_name": "imagem.png",
                "file_type": "image/png",
                "language": "pt"
            }
        """
        if not self.base_url:
            raise ValueError("Orion API URL não configurada")
        
        # Rota correta do Orion: POST /api/ocr/extract
        endpoint = f"{self.base_url}/api/ocr/extract"
        
        file_content, filename, content_type = self._prepare_file(image_file)
        
        files = {
            "file": (filename, file_content, content_type)
        }
        
        # Language é opcional, padrão é "en" no Orion
        data = {}
        if language:
            data["language"] = language
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"📷 Fazendo OCR: {filename} (idioma: {language or 'en'})")
        
        response = requests.post(
            endpoint,
            files=files,
            data=data,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        # Orion retorna {"extracted_text": "texto..."}
        extracted_text = result.get("extracted_text", "")
        logger.info(f"✅ OCR concluído: {len(extracted_text)} caracteres extraídos")
        return result
    
    def process_pdf(
        self,
        pdf_file: Union[str, bytes, BinaryIO],
        extract_text: bool = True,
        extract_images: bool = False
    ) -> Dict[str, Any]:
        """
        Processa PDF extraindo texto e/ou imagens
        
        Args:
            pdf_file: Arquivo PDF (URL, bytes ou file-like object)
            extract_text: Se deve extrair texto
            extract_images: Se deve extrair imagens
            
        Returns:
            Dict com conteúdo extraído
        """
        if not self.base_url:
            raise ValueError("Orion API URL não configurada")
        
        endpoint = f"{self.base_url}/pdf/process"
        
        file_content, filename, content_type = self._prepare_file(pdf_file)
        
        files = {
            "file": (filename, file_content, content_type)
        }
        
        data = {
            "extract_text": extract_text,
            "extract_images": extract_images
        }
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"📄 Processando PDF: {filename}")
        
        response = requests.post(
            endpoint,
            files=files,
            data=data,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"✅ PDF processado: {len(result.get('text', ''))} caracteres extraídos")
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica status do serviço Orion"""
        if not self.base_url:
            return {"status": "unavailable", "error": "URL não configurada"}
        
        endpoint = f"{self.base_url}/health"
        
        try:
            response = requests.get(
                endpoint,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saúde do Orion: {e}")
            return {"status": "unavailable", "error": str(e)}

