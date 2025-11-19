# app/integrations/pydantics_ai/metadados/payloads/ai_payloads.py
"""
Payloads PydanticAI para extração de metadados.

ATENÇÃO: Estes são os modelos que a IA retorna (result_type do Agent).
Todos os campos TÊM Field com descriptions detalhadas para a IA entender
a estrutura esperada do output.

Baseado no prompt de extração de metadados fornecido.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ClassificacaoObrigatoria(BaseModel):
    """
    Classificação obrigatória de todo documento/texto analisado.
    
    A IA DEVE identificar estas informações essenciais.
    """
    tipo_documento: str = Field(
        ...,
        description=(
            "Tipo do documento analisado. Deve ser UM dos seguintes valores: "
            "relatorio_financeiro, contrato, nota_fiscal, parecer_juridico, "
            "manual, politica, apresentacao, email, ata_reuniao, "
            "documentacao_tecnica, especificacao_sistema, guia_implementacao, "
            "persona, briefing_campanha, estrategia_marketing, "
            "processo_operacional, dashboard_marketing, dashboard_vendas, "
            "dashboard_financeiro, relatorio_performance, analise_campanhas, outro. "
            "Se não se encaixar em nenhum, use 'outro'."
        )
    )
    
    categoria: str = Field(
        ...,
        description=(
            "Categoria do documento. Deve ser UMA das seguintes: "
            "financeiro, juridico, fiscal, rh, operacional, marketing, ti, vendas, "
            "produto, estrategia, performance_digital, analytics, business_intelligence, outro. "
            "Escolha a categoria que melhor representa o conteúdo principal."
        )
    )
    
    confidencialidade: str = Field(
        ...,
        description=(
            "Nível de confidencialidade do conteúdo. Deve ser UM dos seguintes: "
            "publico (informação pública), interno (apenas para empresa), "
            "confidencial (acesso restrito), secreto (altamente restrito). "
            "Infira baseado no conteúdo e contexto do texto."
        )
    )


class ConteudoObrigatorio(BaseModel):
    """
    Conteúdo essencial extraído do texto analisado.
    
    Resumo e palavras-chave que capturam a essência do texto.
    """
    resumo_texto: str = Field(
        ...,
        max_length=150,
        description=(
            "Descrição concisa e objetiva do texto analisado. "
            "MÁXIMO 150 caracteres. Deve capturar a ideia principal. "
            "Exemplo: 'Receita Q3 2024 de R$ 2,4M com crescimento de 18%'"
        )
    )
    
    topico_principal: str = Field(
        ...,
        description=(
            "Tópico principal do texto em 2-4 palavras. "
            "Deve ser conciso e direto. "
            "Exemplos: 'receita trimestral', 'contrato prestacao servicos', "
            "'documentacao api rest', 'campanha marketing digital'"
        )
    )
    
    palavras_chave: List[str] = Field(
        ...,
        min_length=3,
        max_length=5,
        description=(
            "3 a 5 palavras-chave mais importantes do texto. "
            "Devem ser substantivos ou termos técnicos relevantes. "
            "NÃO incluir verbos genéricos ou artigos. "
            "Exemplo: ['receita', 'Q3', 'crescimento', 'milhões', 'diretoria']"
        )
    )


class EstruturaDocumento(BaseModel):
    """
    Características estruturais do documento/texto analisado.
    
    Identifica seção, tipo de conteúdo e elementos presentes.
    """
    secao_documento: str = Field(
        ...,
        description=(
            "Seção identificada do documento. Deve ser UMA das seguintes: "
            "introducao, visao_geral, requisitos, metodologia, dados, resultados, "
            "conclusoes, procedimentos, configuracao, implementacao, analise_publico, "
            "pain_points, anexos, outro. "
            "Infira a seção baseado no conteúdo e posição aparente no contexto."
        )
    )
    
    tipo_conteudo: str = Field(
        ...,
        description=(
            "Tipo predominante de conteúdo. Deve ser UM dos seguintes: "
            "narrativo (texto corrido), dados_numericos (números e métricas), "
            "lista_procedimentos (passos ou itens), tabela (dados tabulares), "
            "grafico_descricao (descrição de gráficos), conclusoes (síntese/fechamento), "
            "definicoes (conceitos/termos), especificacao_tecnica (specs técnicas), "
            "codigo (código de programação), checklist (lista de verificação), "
            "analise_persona (perfil de persona), pain_points (dores/problemas), "
            "jornada_cliente (customer journey). "
            "Escolha o tipo que melhor descreve o conteúdo principal."
        )
    )
    
    posicao_estimada: str = Field(
        ...,
        description=(
            "Posição estimada deste texto no documento completo. "
            "Deve ser UM dos seguintes: inicio, meio, fim. "
            "Infira baseado no estilo de escrita: introdutório (inicio), "
            "desenvolvimento (meio), ou conclusivo (fim)."
        )
    )
    
    tem_tabelas: bool = Field(
        default=False,
        description=(
            "True se o texto contém ou referencia tabelas de dados. "
            "False caso contrário."
        )
    )
    
    tem_graficos: bool = Field(
        default=False,
        description=(
            "True se o texto contém, referencia ou descreve gráficos, "
            "visualizações ou charts. False caso contrário."
        )
    )
    
    tem_listas: bool = Field(
        default=False,
        description=(
            "True se o texto contém listas numeradas, bullet points, "
            "ou enumerações. False caso contrário."
        )
    )
    
    tem_dados_quantitativos: bool = Field(
        default=False,
        description=(
            "True se o texto contém números, percentuais, valores, métricas, "
            "ou dados numéricos. False caso contrário."
        )
    )
    
    tem_codigo: bool = Field(
        default=False,
        description=(
            "True se o texto contém trechos de código de programação, "
            "scripts, comandos, ou sintaxe de linguagens. False caso contrário."
        )
    )


class EntidadesExtraidas(BaseModel):
    """
    Entidades nomeadas identificadas no texto.
    
    Extração de informações específicas como datas, valores, pessoas, etc.
    """
    datas: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de TODAS as datas mencionadas no texto. "
            "Pode incluir datas completas (2024-01-15, 15/01/2024), "
            "períodos (Q3 2024, janeiro de 2024), ou referências temporais. "
            "Mantenha o formato original encontrado no texto. "
            "Se não houver datas, retorne lista vazia []"
        )
    )
    
    valores_monetarios: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de TODOS os valores em dinheiro mencionados. "
            "Mantenha o formato original com símbolos e separadores "
            "($1,000, R$ 50.000, € 2.500, 1.5 milhões). "
            "Se não houver valores, retorne lista vazia []"
        )
    )
    
    pessoas: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de nomes de TODAS as pessoas mencionadas no texto. "
            "Inclua nomes completos ou parciais identificados. "
            "Exemplos: 'João Silva', 'Maria Santos', 'Dr. Pedro'. "
            "Se não houver pessoas, retorne lista vazia []"
        )
    )
    
    empresas: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de TODAS as empresas, organizações ou instituições mencionadas. "
            "Inclua nomes de empresas, marcas, órgãos governamentais. "
            "Exemplos: 'Google', 'Microsoft', 'BNDES', 'Receita Federal'. "
            "Se não houver empresas, retorne lista vazia []"
        )
    )
    
    localizacoes: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de TODAS as localizações geográficas mencionadas. "
            "Inclua cidades, estados, países, regiões, endereços. "
            "Exemplos: 'São Paulo', 'Brasil', 'Escritório Central', 'Região Sudeste'. "
            "Se não houver localizações, retorne lista vazia []"
        )
    )


class ContextoTemporal(BaseModel):
    """
    Informações sobre o contexto temporal do texto.
    
    Identifica período de referência e natureza temporal do conteúdo.
    """
    periodo_referencia: Optional[str] = Field(
        None,
        description=(
            "Período que o texto se refere ou analisa. "
            "Exemplos: 'Q3 2024', 'janeiro de 2024', '2023-2024', 'ano fiscal 2024'. "
            "Se não for possível identificar, use null."
        )
    )
    
    data_vencimento: Optional[str] = Field(
        None,
        description=(
            "Data de vencimento, prazo ou deadline mencionado. "
            "Aplicável principalmente para contratos, prazos, entregas. "
            "Formato original do texto. "
            "Se não aplicável, use null."
        )
    )
    
    temporalidade: str = Field(
        ...,
        description=(
            "Natureza temporal do conteúdo. Deve ser UM dos seguintes: "
            "passado (eventos/dados do passado, análise histórica), "
            "presente (situação atual, status presente), "
            "futuro (projeções, planos, previsões), "
            "atemporal (conceitos, definições, procedimentos sem tempo específico). "
            "Escolha o que melhor representa o foco temporal do texto."
        )
    )


class MetadadosEspecificos(BaseModel):
    """
    Metadados específicos variáveis por tipo de documento.
    
    Campos opcionais que podem ou não estar presentes dependendo
    do tipo e conteúdo do documento. Use null quando não aplicável.
    """
    numero_documento: Optional[str] = Field(
        None,
        description=(
            "Número identificador do documento se mencionado. "
            "Exemplos: número de contrato, nota fiscal, processo. "
            "Se não houver, use null."
        )
    )
    
    versao: Optional[str] = Field(
        None,
        description=(
            "Versão do documento se mencionada. "
            "Exemplos: '1.0', 'v2.3', 'draft', 'final'. "
            "Se não houver, use null."
        )
    )
    
    status: Optional[str] = Field(
        None,
        description=(
            "Status do documento se identificável. "
            "Deve ser UM dos seguintes ou null: rascunho, revisao, aprovado, cancelado. "
            "Infira do conteúdo ou use null se não aplicável."
        )
    )
    
    departamento_origem: Optional[str] = Field(
        None,
        description=(
            "Departamento ou área que originou/é responsável pelo documento. "
            "Exemplos: 'financeiro', 'juridico', 'ti', 'marketing', 'rh'. "
            "Infira do conteúdo ou use null."
        )
    )
    
    audiencia_alvo: Optional[str] = Field(
        None,
        description=(
            "Público-alvo ou audiência do documento. Deve ser UM dos seguintes ou null: "
            "desenvolvedores, analistas_dados, gerentes, diretoria, equipe_marketing, "
            "clientes_externos, stakeholders, profissionais_ti, estudantes_ti, "
            "consultores, todos_funcionarios. "
            "Infira baseado no tom, vocabulário e conteúdo."
        )
    )
    
    complexidade_tecnica: Optional[str] = Field(
        None,
        description=(
            "Nível de complexidade técnica para documentos técnicos. "
            "Deve ser UM dos seguintes ou null: basica, intermediaria, avancada. "
            "Avalie baseado no vocabulário técnico e profundidade. "
            "Aplicável principalmente para documentação técnica."
        )
    )
    
    tecnologias_mencionadas: List[str] = Field(
        default_factory=list,
        description=(
            "Lista de tecnologias, ferramentas, linguagens ou frameworks mencionados. "
            "Exemplos: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS']. "
            "Se não houver tecnologias, retorne lista vazia []"
        )
    )
    
    publico_alvo_persona: Optional[str] = Field(
        None,
        description=(
            "Para documentos de persona/marketing: perfil do público-alvo. "
            "Deve ser UM dos seguintes ou null: profissionais_ti, desenvolvedores, "
            "gestores, estudantes, consultores. "
            "Use apenas se o documento for sobre personas."
        )
    )
    
    tipo_analise_marketing: Optional[str] = Field(
        None,
        description=(
            "Para documentos de marketing/análise: tipo de análise realizada. "
            "Deve ser UM dos seguintes ou null: pain_points, jornada_cliente, "
            "perfil_demografico, estrategia_campanha. "
            "Use apenas se for documento de marketing/análise."
        )
    )
    
    plataforma_dashboard: Optional[str] = Field(
        None,
        description=(
            "Para dashboards/relatórios de plataformas: origem dos dados. "
            "Deve ser UM dos seguintes ou null: facebook_ads, google_ads, pipedrive, "
            "hubspot, salesforce, power_bi, tableau, voomp. "
            "Use apenas se for relatório/dashboard de plataforma específica."
        )
    )
    
    metricas_principais: List[str] = Field(
        default_factory=list,
        description=(
            "KPIs ou métricas principais identificadas no texto. "
            "Exemplos: ['CPL', 'CPA', 'CTR', 'conversão', 'ROI', 'receita', 'lucro']. "
            "Foque em siglas e termos de métricas de negócio. "
            "Se não houver métricas, retorne lista vazia []"
        )
    )
    
    periodo_analise: Optional[str] = Field(
        None,
        description=(
            "Período específico dos dados analisados em relatórios. "
            "Exemplos: 'Q3 2024', 'Janeiro-Março 2024', 'Ano Fiscal 2023'. "
            "Diferente de periodo_referencia (contexto temporal geral). "
            "Use null se não aplicável."
        )
    )
    
    moeda_valores: Optional[str] = Field(
        None,
        description=(
            "Moeda predominante dos valores monetários mencionados. "
            "Deve ser código ISO ou null: BRL, USD, EUR, GBP, etc. "
            "Infira da maioria dos valores no texto."
        )
    )


class MetadadoAIPayload(BaseModel):
    """
    Payload completo retornado pelo PydanticAI Agent.
    
    Este é o result_type do Agent. A IA DEVE preencher todos os campos
    obrigatórios e pode deixar campos opcionais como null/lista vazia
    quando não aplicável.
    
    IMPORTANTE: Responda APENAS com JSON válido estruturado conforme
    este schema. Não inclua explicações ou comentários adicionais.
    """
    classificacao_obrigatoria: ClassificacaoObrigatoria = Field(
        ...,
        description="Classificação essencial: tipo, categoria e confidencialidade"
    )
    
    conteudo_obrigatorio: ConteudoObrigatorio = Field(
        ...,
        description="Resumo, tópico e palavras-chave do conteúdo"
    )
    
    estrutura_documento: EstruturaDocumento = Field(
        ...,
        description="Características estruturais e elementos presentes"
    )
    
    entidades_extraidas: EntidadesExtraidas = Field(
        default_factory=EntidadesExtraidas,
        description="Entidades nomeadas identificadas (datas, valores, pessoas, etc)"
    )
    
    contexto_temporal: ContextoTemporal = Field(
        ...,
        description="Informações sobre período e temporalidade"
    )
    
    metadados_especificos: MetadadosEspecificos = Field(
        default_factory=MetadadosEspecificos,
        description="Metadados variáveis específicos do tipo de documento"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "classificacao_obrigatoria": {
                    "tipo_documento": "relatorio_financeiro",
                    "categoria": "financeiro",
                    "confidencialidade": "interno"
                },
                "conteudo_obrigatorio": {
                    "resumo_texto": "Receita Q3 2024 de R$ 2,4M com crescimento de 18%",
                    "topico_principal": "receita trimestral",
                    "palavras_chave": ["receita", "Q3", "crescimento", "milhões", "diretoria"]
                },
                "estrutura_documento": {
                    "secao_documento": "resultados",
                    "tipo_conteudo": "dados_numericos",
                    "posicao_estimada": "meio",
                    "tem_tabelas": False,
                    "tem_graficos": False,
                    "tem_listas": False,
                    "tem_dados_quantitativos": True,
                    "tem_codigo": False
                },
                "entidades_extraidas": {
                    "datas": ["terceiro trimestre de 2024", "15 de outubro de 2024"],
                    "valores_monetarios": ["R$ 2,4 milhões"],
                    "pessoas": ["Maria Silva"],
                    "empresas": [],
                    "localizacoes": []
                },
                "contexto_temporal": {
                    "periodo_referencia": "Q3 2024",
                    "data_vencimento": None,
                    "temporalidade": "passado"
                },
                "metadados_especificos": {
                    "numero_documento": None,
                    "versao": None,
                    "status": "aprovado",
                    "departamento_origem": "financeiro",
                    "audiencia_alvo": "diretoria",
                    "complexidade_tecnica": None,
                    "tecnologias_mencionadas": [],
                    "publico_alvo_persona": None,
                    "tipo_analise_marketing": None,
                    "plataforma_dashboard": None,
                    "metricas_principais": [],
                    "periodo_analise": None,
                    "moeda_valores": "BRL"
                }
            }
        }