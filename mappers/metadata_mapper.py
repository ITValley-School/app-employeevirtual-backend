"""
Mapper para metadata
Converte entre Entity (domínio) e Response (API)
Seguindo padrão IT Valley Architecture
"""
from typing import Dict, Any
from datetime import datetime

from schemas.metadata.response import MetadadosResponse as MetadataResponse


class MetadataMapper:
    """Mapper para conversão de metadata"""
    
    @staticmethod
    def to_response(data: Dict[str, Any]) -> MetadataResponse:
        """
        Converte dados para MetadataResponse
        
        Args:
            data: Dados dos metadados
            
        Returns:
            MetadataResponse: Metadados formatados
        """
        return MetadataResponse(
            id=data.get("id", ""),
            tipo_documento=data.get("tipo_documento", "texto"),
            categoria=data.get("categoria", "geral"),
            confidencialidade=data.get("confidencialidade", "publico"),
            resumo_texto=data.get("resumo_texto", ""),
            topico_principal=data.get("topico_principal", ""),
            palavras_chave=data.get("palavras_chave", []),
            secao_documento=data.get("secao_documento", "corpo"),
            tipo_conteudo=data.get("tipo_conteudo", "texto"),
            posicao_estimada=data.get("posicao_estimada", "inicio"),
            tem_tabelas=data.get("tem_tabelas", False),
            tem_graficos=data.get("tem_graficos", False),
            tem_listas=data.get("tem_listas", False),
            tem_dados_quantitativos=data.get("tem_dados_quantitativos", False),
            tem_codigo=data.get("tem_codigo", False),
            entidades_extraidas=data.get("entidades_extraidas", {}),
            contexto_temporal=data.get("contexto_temporal", {}),
            metadados_especificos=data.get("metadados_especificos", {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
