# app/domain/metadados/metadado_entity.py
"""
Entity de Metadados - Domain do sistema.

Representa metadados extraídos de documentos/chunks.
Dataclass puro - SEM Pydantic (Pydantic só em Payloads e Schemas).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any


def _get(data: Any, name: str, default=None):
    """
    Helper para extrair dados de qualquer fonte (dict, objeto, etc).
    Usado em métodos que recebem "Any" como DTO.
    """
    if isinstance(data, dict):
        return data.get(name, default)
    return getattr(data, name, default)


@dataclass
class Metadado:
    """
    Entity de Metadados extraídos de texto.
    
    Representa metadados estruturados que podem vir de:
    - Um chunk de documento
    - Um documento completo
    - Qualquer texto analisado
    
    Campos estruturados para queries + dicts flexíveis para extensibilidade.
    """
    
    # ===== IDENTIFICAÇÃO =====
    id: str
    
    # ===== CLASSIFICAÇÃO OBRIGATÓRIA =====
    tipo_documento: str  # relatorio_financeiro, contrato, nota_fiscal, etc
    categoria: str       # financeiro, juridico, fiscal, rh, operacional, etc
    confidencialidade: str  # publico, interno, confidencial, secreto
    
    # ===== CONTEÚDO OBRIGATÓRIO =====
    resumo_texto: str        # Resumo do texto analisado (máx 150 chars)
    topico_principal: str    # Tópico principal (2-4 palavras)
    palavras_chave: List[str]  # 3-5 palavras mais importantes
    
    # ===== ESTRUTURA DO DOCUMENTO =====
    secao_documento: str   # introducao, resultados, conclusoes, etc
    tipo_conteudo: str     # narrativo, dados_numericos, tabela, etc
    posicao_estimada: str  # inicio, meio, fim
    
    # Flags de características
    tem_tabelas: bool = False
    tem_graficos: bool = False
    tem_listas: bool = False
    tem_dados_quantitativos: bool = False
    tem_codigo: bool = False
    
    # ===== DADOS FLEXÍVEIS (JSON) =====
    entidades_extraidas: dict = field(default_factory=dict)
    # Exemplo: {
    #   "datas": ["2024-01-15", "Q3 2024"],
    #   "valores_monetarios": ["R$ 50.000", "$1,000"],
    #   "pessoas": ["João Silva", "Maria Santos"],
    #   "empresas": ["Google", "Microsoft"],
    #   "localizacoes": ["São Paulo", "Brasil"]
    # }
    
    contexto_temporal: dict = field(default_factory=dict)
    # Exemplo: {
    #   "periodo_referencia": "Q3 2024",
    #   "data_vencimento": "2025-12-31",
    #   "temporalidade": "passado"
    # }
    
    metadados_especificos: dict = field(default_factory=dict)
    # Exemplo: {
    #   "numero_documento": "123",
    #   "versao": "1.0",
    #   "status": "aprovado",
    #   "departamento_origem": "financeiro",
    #   "audiencia_alvo": "diretoria",
    #   "tecnologias_mencionadas": ["Python", "FastAPI"],
    #   "metricas_principais": ["CPL", "CPA"],
    #   "moeda_valores": "BRL"
    # }
    
    # ===== AUDITORIA =====
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # ===== REGRAS DE NEGÓCIO =====
    
    def validar(self) -> None:
        """
        Valida todas as regras de negócio da entity.
        Lança ValueError se alguma regra for violada.
        """
        self._validar_classificacao()
        self._validar_conteudo_obrigatorio()
        self._validar_estrutura()
    
    def _validar_classificacao(self) -> None:
        """Valida campos de classificação obrigatória"""
        tipos_validos = [
            "relatorio_financeiro", "contrato", "nota_fiscal", "parecer_juridico",
            "manual", "politica", "apresentacao", "email", "ata_reuniao",
            "documentacao_tecnica", "especificacao_sistema", "guia_implementacao",
            "persona", "briefing_campanha", "estrategia_marketing",
            "processo_operacional", "dashboard_marketing", "dashboard_vendas",
            "dashboard_financeiro", "relatorio_performance", "analise_campanhas", "outro"
        ]
        
        if self.tipo_documento not in tipos_validos:
            raise ValueError(
                f"Tipo de documento inválido: '{self.tipo_documento}'. "
                f"Deve ser um de: {', '.join(tipos_validos[:5])}..."
            )
        
        categorias_validas = [
            "financeiro", "juridico", "fiscal", "rh", "operacional",
            "marketing", "ti", "vendas", "produto", "estrategia",
            "performance_digital", "analytics", "business_intelligence", "outro"
        ]
        
        if self.categoria not in categorias_validas:
            raise ValueError(
                f"Categoria inválida: '{self.categoria}'. "
                f"Deve ser uma de: {', '.join(categorias_validas)}"
            )
        
        confidencialidades_validas = ["publico", "interno", "confidencial", "secreto"]
        
        if self.confidencialidade not in confidencialidades_validas:
            raise ValueError(
                f"Confidencialidade inválida: '{self.confidencialidade}'. "
                f"Deve ser: {', '.join(confidencialidades_validas)}"
            )
    
    def _validar_conteudo_obrigatorio(self) -> None:
        """Valida campos de conteúdo obrigatório"""
        if not self.resumo_texto or len(self.resumo_texto.strip()) == 0:
            raise ValueError("Resumo do texto é obrigatório")
        
        if len(self.resumo_texto) > 150:
            raise ValueError(
                f"Resumo deve ter no máximo 150 caracteres. "
                f"Atual: {len(self.resumo_texto)}"
            )
        
        if not self.topico_principal or len(self.topico_principal.strip()) < 2:
            raise ValueError("Tópico principal deve ter pelo menos 2 caracteres")
        
        if not self.palavras_chave or len(self.palavras_chave) < 3:
            raise ValueError(
                f"Deve ter pelo menos 3 palavras-chave. "
                f"Atual: {len(self.palavras_chave) if self.palavras_chave else 0}"
            )
        
        if len(self.palavras_chave) > 5:
            raise ValueError(
                f"Deve ter no máximo 5 palavras-chave. "
                f"Atual: {len(self.palavras_chave)}"
            )
    
    def _validar_estrutura(self) -> None:
        """Valida campos de estrutura do documento"""
        secoes_validas = [
            "introducao", "visao_geral", "requisitos", "metodologia", "dados",
            "resultados", "conclusoes", "procedimentos", "configuracao",
            "implementacao", "analise_publico", "pain_points", "anexos", "outro"
        ]
        
        if self.secao_documento not in secoes_validas:
            raise ValueError(
                f"Seção de documento inválida: '{self.secao_documento}'. "
                f"Deve ser uma de: {', '.join(secoes_validas[:5])}..."
            )
        
        tipos_conteudo_validos = [
            "narrativo", "dados_numericos", "lista_procedimentos", "tabela",
            "grafico_descricao", "conclusoes", "definicoes", "especificacao_tecnica",
            "codigo", "checklist", "analise_persona", "pain_points", "jornada_cliente"
        ]
        
        if self.tipo_conteudo not in tipos_conteudo_validos:
            raise ValueError(
                f"Tipo de conteúdo inválido: '{self.tipo_conteudo}'"
            )
        
        posicoes_validas = ["inicio", "meio", "fim"]
        
        if self.posicao_estimada not in posicoes_validas:
            raise ValueError(
                f"Posição estimada inválida: '{self.posicao_estimada}'. "
                f"Deve ser: {', '.join(posicoes_validas)}"
            )
    
    # ===== MÉTODOS DE NEGÓCIO =====
    
    def adicionar_entidade(self, tipo: str, valor: str) -> None:
        """
        Adiciona uma entidade extraída.
        
        Args:
            tipo: Tipo da entidade (datas, valores_monetarios, pessoas, empresas, localizacoes)
            valor: Valor da entidade
            
        Raises:
            ValueError: Se tipo inválido
        """
        tipos_validos = ["datas", "valores_monetarios", "pessoas", "empresas", "localizacoes"]
        
        if tipo not in tipos_validos:
            raise ValueError(
                f"Tipo de entidade inválido: '{tipo}'. "
                f"Deve ser: {', '.join(tipos_validos)}"
            )
        
        if tipo not in self.entidades_extraidas:
            self.entidades_extraidas[tipo] = []
        
        if valor not in self.entidades_extraidas[tipo]:
            self.entidades_extraidas[tipo].append(valor)
        
        self.updated_at = datetime.utcnow()
    
    def atualizar_contexto_temporal(
        self,
        periodo: Optional[str] = None,
        vencimento: Optional[str] = None,
        temporalidade: Optional[str] = None
    ) -> None:
        """
        Atualiza informações de contexto temporal.
        
        Args:
            periodo: Período de referência (ex: "Q3 2024")
            vencimento: Data de vencimento
            temporalidade: passado, presente, futuro, atemporal
            
        Raises:
            ValueError: Se temporalidade inválida
        """
        if periodo is not None:
            self.contexto_temporal["periodo_referencia"] = periodo
        
        if vencimento is not None:
            self.contexto_temporal["data_vencimento"] = vencimento
        
        if temporalidade is not None:
            temporalidades_validas = ["passado", "presente", "futuro", "atemporal"]
            if temporalidade not in temporalidades_validas:
                raise ValueError(
                    f"Temporalidade inválida: '{temporalidade}'. "
                    f"Deve ser: {', '.join(temporalidades_validas)}"
                )
            self.contexto_temporal["temporalidade"] = temporalidade
        
        self.updated_at = datetime.utcnow()
    
    def adicionar_metadado_especifico(self, chave: str, valor: Any) -> None:
        """
        Adiciona um metadado específico (campo flexível).
        
        Args:
            chave: Nome do metadado
            valor: Valor do metadado
        """
        self.metadados_especificos[chave] = valor
        self.updated_at = datetime.utcnow()
    
    def aplicar_atualizacao_from_any(self, data: Any) -> None:
        """
        Aplica atualizações parciais de qualquer fonte de dados.
        Usado para updates parciais vindos de DTOs, dicts, etc.
        
        Args:
            data: Objeto com dados para atualizar (DTO, dict, etc)
        """
        # Atualizar campos simples se presentes
        novo_resumo = _get(data, "resumo_texto")
        if novo_resumo is not None:
            if len(novo_resumo) > 150:
                raise ValueError("Resumo deve ter no máximo 150 caracteres")
            self.resumo_texto = novo_resumo.strip()
        
        novo_topico = _get(data, "topico_principal")
        if novo_topico is not None:
            self.topico_principal = novo_topico.strip()
        
        novas_palavras = _get(data, "palavras_chave")
        if novas_palavras is not None:
            if len(novas_palavras) < 3 or len(novas_palavras) > 5:
                raise ValueError("Deve ter entre 3 e 5 palavras-chave")
            self.palavras_chave = novas_palavras
        
        # Atualizar dicts flexíveis (merge)
        novas_entidades = _get(data, "entidades_extraidas")
        if novas_entidades is not None:
            self.entidades_extraidas.update(novas_entidades)
        
        novo_contexto = _get(data, "contexto_temporal")
        if novo_contexto is not None:
            self.contexto_temporal.update(novo_contexto)
        
        novos_especificos = _get(data, "metadados_especificos")
        if novos_especificos is not None:
            self.metadados_especificos.update(novos_especificos)
        
        self.updated_at = datetime.utcnow()