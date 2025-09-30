# schemas/metadados/responses.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class EntidadesExtraidasResponse(BaseModel):
    """
    Entidades extraídas - ESTRUTURADO.
    
    Sempre tem os mesmos campos possíveis.
    """
    datas: List[str] = Field(
        default_factory=list,
        description="Datas mencionadas no texto"
    )
    valores_monetarios: List[str] = Field(
        default_factory=list,
        description="Valores em dinheiro"
    )
    pessoas: List[str] = Field(
        default_factory=list,
        description="Nomes de pessoas"
    )
    empresas: List[str] = Field(
        default_factory=list,
        description="Nomes de empresas/organizações"
    )
    localizacoes: List[str] = Field(
        default_factory=list,
        description="Lugares mencionados"
    )


class ContextoTemporalResponse(BaseModel):
    """
    Contexto temporal - ESTRUTURADO.
    
    Campos previsíveis.
    """
    periodo_referencia: Optional[str] = Field(
        None,
        description="Período de referência (Q3 2024, etc)"
    )
    data_vencimento: Optional[str] = Field(
        None,
        description="Data de vencimento se aplicável"
    )
    temporalidade: str = Field(
        ...,
        description="Natureza temporal: passado, presente, futuro, atemporal"
    )


class MetadadosResponse(BaseModel):
    """
    Response completo de metadados.
    """
    id: str
    
    # Campos obrigatórios estruturados
    tipo_documento: str
    categoria: str
    confidencialidade: str
    resumo_texto: str
    topico_principal: str
    palavras_chave: List[str]
    
    secao_documento: str
    tipo_conteudo: str
    posicao_estimada: str
    
    tem_tabelas: bool
    tem_graficos: bool
    tem_listas: bool
    tem_dados_quantitativos: bool
    tem_codigo: bool
    
    # Estruturados (classes) - previsíveis
    entidades_extraidas: EntidadesExtraidasResponse = Field(
        default_factory=EntidadesExtraidasResponse,
        description="Entidades identificadas no texto"
    )
    contexto_temporal: ContextoTemporalResponse = Field(
        ...,
        description="Informações temporais"
    )
    
    # Dict genérico - totalmente variável
    metadados_especificos: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Metadados específicos variáveis por tipo de documento. "
            "Pode conter: numero_documento, versao, status, "
            "departamento_origem, audiencia_alvo, tecnologias_mencionadas, "
            "metricas_principais, moeda_valores, etc."
        )
    )
    
    # Auditoria
    created_at: datetime
    updated_at: datetime