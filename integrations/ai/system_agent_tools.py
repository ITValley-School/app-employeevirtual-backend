"""
Sistema de ferramentas para agentes de sistema
Constrói agentes Pydantic AI com ferramentas avançadas
"""
from __future__ import annotations

import logging
import base64
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from pydantic_ai import Agent as PydanticAgent, RunContext
from integrations.ai.orion_client import OrionClient
from domain.agents.agent_tools import ToolType

logger = logging.getLogger(__name__)


@dataclass
class SystemAgentDependencies:
    """Dependências para agentes de sistema com ferramentas avançadas"""
    agent_id: str
    user_id: str
    orion_client: Optional[OrionClient] = None
    file_context: Optional[Dict[str, Any]] = None  # Contexto do arquivo anexado
    # Outras dependências podem ser adicionadas aqui (RAG, cache, etc.)


def build_system_agent(
    system_prompt: str,
    enabled_tools: List[str],
    orion_client: Optional[OrionClient] = None
) -> PydanticAgent[SystemAgentDependencies]:
    """
    Constrói agente de sistema com ferramentas avançadas
    
    Args:
        system_prompt: Prompt do sistema
        enabled_tools: Lista de ferramentas habilitadas
        orion_client: Cliente Orion (opcional)
        
    Returns:
        Agent configurado com ferramentas
    """
    agent = PydanticAgent(
        model="openai:gpt-4o-mini",
        system_prompt=system_prompt,
        deps_type=SystemAgentDependencies,
    )
    
    # Registra ferramentas baseado na lista enabled_tools
    if ToolType.TRANSCRIBE_AUDIO in enabled_tools:
        @agent.tool
        def transcribe_audio(
            context: RunContext[SystemAgentDependencies],
            audio_url: Optional[str] = None,
            language: str = "pt"
        ) -> str:
            """
            Transcreve áudio de um arquivo ou URL.
            Use esta ferramenta quando o usuário pedir para transcrever áudio, gravações ou arquivos de som.
            
            Args:
                audio_url: URL ou caminho do arquivo de áudio (opcional se arquivo foi anexado)
                language: Idioma do áudio (pt, en, es, etc.)
                
            Returns:
                Texto transcrito do áudio
            """
            if not context.deps.orion_client:
                return "Erro: Serviço de transcrição não disponível. Verifique a configuração do Orion."
            
            try:
                # Verifica se há arquivo anexado nas dependências
                file_content = None
                file_name = None
                
                if context.deps.file_context and context.deps.file_context.get('has_file'):
                    file_content = base64.b64decode(context.deps.file_context['file_content_base64'])
                    file_name = context.deps.file_context.get('file_name', 'audio.mp3')
                    logger.info(f"📎 Usando arquivo anexado: {file_name} ({len(file_content)} bytes)")
                
                # Se tem arquivo anexado, usa ele; senão usa a URL
                if file_content:
                    logger.info(f"🎤 Transcrevendo áudio anexado: {file_name} (idioma: {language})")
                    result = context.deps.orion_client.transcribe_audio(
                        file_content,  # Passa bytes diretamente
                        language=language
                    )
                elif audio_url:
                    logger.info(f"🎤 Transcrevendo áudio: {audio_url} (idioma: {language})")
                    result = context.deps.orion_client.transcribe_audio(
                        audio_url,
                        language=language
                    )
                else:
                    return "Erro: É necessário fornecer uma URL de áudio ou anexar um arquivo de áudio."
                
                # Orion retorna {"transcription": "texto..."}
                transcript = result.get("transcription", "")
                if not transcript:
                    return "Não foi possível transcrever o áudio. O arquivo pode estar corrompido ou em formato não suportado."
                
                return f"Transcrição do áudio:\n\n{transcript}"
            except Exception as e:
                logger.error(f"Erro ao transcrever áudio: {e}", exc_info=True)
                return f"Erro ao transcrever áudio: {str(e)}"
    
    if ToolType.TRANSCRIBE_YOUTUBE in enabled_tools:
        @agent.tool
        def transcribe_youtube(
            context: RunContext[SystemAgentDependencies],
            youtube_url: str,
            language: str = "pt"
        ) -> str:
            """
            Transcreve vídeo do YouTube.
            Use esta ferramenta quando o usuário pedir para transcrever um vídeo do YouTube.
            
            Args:
                youtube_url: URL do vídeo do YouTube
                language: Idioma do vídeo
                
            Returns:
                Texto transcrito do vídeo
            """
            if not context.deps.orion_client:
                return "Erro: Serviço de transcrição não disponível. Verifique a configuração do Orion."
            
            try:
                logger.info(f"📺 Transcrevendo YouTube: {youtube_url} (idioma: {language})")
                result = context.deps.orion_client.transcribe_youtube(
                    youtube_url,
                    language=language
                )
                
                # Orion retorna {"transcription": "texto...", "method": "direct", ...}
                transcript = result.get("transcription", "")
                method = result.get("method", "unknown")
                
                if not transcript:
                    return "Não foi possível transcrever o vídeo. Verifique se a URL é válida e se o vídeo está acessível."
                
                method_info = f" (método: {method})" if method != "unknown" else ""
                return f"Transcrição do YouTube{method_info}:\n\n{transcript}"
            except Exception as e:
                logger.error(f"Erro ao transcrever YouTube: {e}", exc_info=True)
                return f"Erro ao transcrever YouTube: {str(e)}"
    
    if ToolType.OCR_IMAGE in enabled_tools:
        @agent.tool
        def ocr_image(
            context: RunContext[SystemAgentDependencies],
            image_url: Optional[str] = None,
            language: str = "en"
        ) -> str:
            """
            Extrai texto de uma imagem usando OCR.
            Use esta ferramenta quando o usuário pedir para extrair texto de imagens, screenshots ou documentos escaneados.
            
            Args:
                image_url: URL ou caminho da imagem (opcional se arquivo foi anexado)
                language: Idioma para OCR (padrão: "en", suporta: pt, en, es, etc.)
                
            Returns:
                Texto extraído da imagem
            """
            if not context.deps.orion_client:
                return "Erro: Serviço OCR não disponível. Verifique a configuração do Orion."
            
            try:
                # Verifica se há arquivo anexado nas dependências
                file_content = None
                file_name = None
                
                if context.deps.file_context and context.deps.file_context.get('has_file'):
                    file_content = base64.b64decode(context.deps.file_context['file_content_base64'])
                    file_name = context.deps.file_context.get('file_name', 'imagem.png')
                    logger.info(f"📎 Usando imagem anexada: {file_name} ({len(file_content)} bytes)")
                
                # Se tem arquivo anexado, usa ele; senão usa a URL
                if file_content:
                    logger.info(f"📷 Fazendo OCR de imagem anexada: {file_name} (idioma: {language})")
                    result = context.deps.orion_client.ocr_image(
                        file_content,  # Passa bytes diretamente
                        language=language
                    )
                elif image_url:
                    logger.info(f"📷 Fazendo OCR: {image_url} (idioma: {language})")
                    result = context.deps.orion_client.ocr_image(
                        image_url,
                        language=language
                    )
                else:
                    return "Erro: É necessário fornecer uma URL de imagem ou anexar um arquivo de imagem."
                
                # Orion retorna {"extracted_text": "texto..."}
                extracted_text = result.get("extracted_text", "")
                if not extracted_text:
                    return "Não foi possível extrair texto da imagem. A imagem pode não conter texto legível."
                
                result_file_name = result.get("file_name", file_name or "imagem")
                file_type = result.get("file_type", "")
                return f"Texto extraído da imagem ({result_file_name}{f' - {file_type}' if file_type else ''}):\n\n{extracted_text}"
            except Exception as e:
                logger.error(f"Erro ao fazer OCR: {e}", exc_info=True)
                return f"Erro ao fazer OCR: {str(e)}"
    
    if ToolType.PROCESS_PDF in enabled_tools:
        @agent.tool
        def process_pdf(
            context: RunContext[SystemAgentDependencies],
            pdf_url: Optional[str] = None,
            extract_text: bool = True,
            extract_images: bool = False
        ) -> str:
            """
            Processa PDF extraindo texto e/ou imagens.
            Use esta ferramenta quando o usuário pedir para processar, extrair texto ou analisar um PDF.
            
            Args:
                pdf_url: URL ou caminho do PDF (opcional se arquivo foi anexado)
                extract_text: Se deve extrair texto (padrão: True)
                extract_images: Se deve extrair imagens (padrão: False)
                
            Returns:
                Conteúdo extraído do PDF
            """
            if not context.deps.orion_client:
                return "Erro: Serviço de processamento de PDF não disponível. Verifique a configuração do Orion."
            
            try:
                # Verifica se há arquivo anexado nas dependências
                file_content = None
                file_name = None
                
                if context.deps.file_context and context.deps.file_context.get('has_file'):
                    file_content = base64.b64decode(context.deps.file_context['file_content_base64'])
                    file_name = context.deps.file_context.get('file_name', 'documento.pdf')
                    logger.info(f"📎 Usando PDF anexado: {file_name} ({len(file_content)} bytes)")
                
                # Se tem arquivo anexado, usa ele; senão usa a URL
                if file_content:
                    logger.info(f"📄 Processando PDF anexado: {file_name}")
                    result = context.deps.orion_client.process_pdf(
                        file_content,  # Passa bytes diretamente
                        extract_text=extract_text,
                        extract_images=extract_images
                    )
                elif pdf_url:
                    logger.info(f"📄 Processando PDF: {pdf_url}")
                    result = context.deps.orion_client.process_pdf(
                        pdf_url,
                        extract_text=extract_text,
                        extract_images=extract_images
                    )
                else:
                    return "Erro: É necessário fornecer uma URL de PDF ou anexar um arquivo PDF."
                
                text = result.get("text", result.get("extracted_text", ""))
                if not text and extract_text:
                    return "Não foi possível extrair texto do PDF. O arquivo pode estar corrompido ou protegido."
                
                images_info = ""
                if extract_images and result.get("images"):
                    images_count = len(result.get("images", []))
                    images_info = f"\n\n{images_count} imagem(ns) extraída(s)."
                
                return f"Conteúdo extraído do PDF:\n\n{text}{images_info}"
            except Exception as e:
                logger.error(f"Erro ao processar PDF: {e}", exc_info=True)
                return f"Erro ao processar PDF: {str(e)}"
    
    return agent

