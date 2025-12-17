"""
Tipos de ferramentas disponíveis para agentes
"""
from enum import Enum


class ToolType(str, Enum):
    """Tipos de ferramentas disponíveis"""
    # Ferramentas básicas (todos os agentes)
    RAG_RETRIEVE = "rag_retrieve"
    CONVERSATION_HISTORY = "conversation_history"
    
    # Ferramentas avançadas (apenas agentes de sistema)
    TRANSCRIBE_AUDIO = "transcribe_audio"
    TRANSCRIBE_YOUTUBE = "transcribe_youtube"
    OCR_IMAGE = "ocr_image"
    PROCESS_PDF = "process_pdf"
    EXTRACT_TEXT = "extract_text"
    ANALYZE_DOCUMENT = "analyze_document"

