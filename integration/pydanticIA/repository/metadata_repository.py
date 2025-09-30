# app/integration/pydanticIA/repositories/pydantic_ai_repository.py
"""
Repository corrigido para PydanticAI.
❌ ERRO ORIGINAL: BaseModel + __init__ com self.agent não funciona
✅ SOLUÇÃO: Classe normal OU BaseModel com field declarado
"""

from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import Optional
from integration.pydanticIA.payload.response import MetadadoAIPayload
from integration.pydanticIA.payload.request import MetadataRequest


# ===== OPÇÃO 1: CLASSE PYTHON NORMAL (RECOMENDADA) =====

class PydanticAIRepository:
    """
    ✅ Repository como classe Python normal.
    Mais simples e direto para este caso.
    """
    
    def __init__(self):
        self.agent = Agent('openai:gpt-4o-mini')

    async def create_metadata(self, request: MetadataRequest) -> MetadadoAIPayload:
        """
        Extrai metadados do texto extraído do PDF.
        
        Args:
            request: Request com trecho do PDF
            
        Returns:
            MetadadoAIPayload: Metadados extraídos
        """
        try:
            # ✅ Passa apenas o texto, não o objeto request completo
            response = await self.agent.run(request.trecho_pdf_em_string,     
                output_type=MetadadoAIPayload
            )
            
            print(f"✅ Metadados extraídos: {response.data}")
            
            # ✅ response.data (não response.output)
            return response.data
            
        except Exception as e:
            print(f"❌ Erro na extração: {e}")
            raise ValueError(f"Falha na extração de metadados: {str(e)}")