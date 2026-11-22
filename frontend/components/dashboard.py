"""Componente responsável pela renderização do painel de dados.

O usuário escolhe quais visões (resumo, gráficos, tabela) e quais gráficos
deseja visualizar. Para adicionar um gráfico, crie a função de renderização
e registre-a em CATALOGO_GRAFICOS.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict

import numpy as np
import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

LIMITE_REGISTROS_GRAFICO = 1_000
LIMITE_CATEGORIAS = 15
ALTURA_GRAFICO = 340
QUANTIDADE_MAXIMA_FAIXAS = 12

# Visões disponíveis no painel
VISAO_RESUMO = "Resumo"
VISAO_GRAFICOS = "Gráficos"
VISAO_TABELA = "Tabela de dados"
VISOES = (VISAO_RESUMO, VISAO_GRAFICOS, VISAO_TABELA)
VISOES_PADRAO = [VISAO_RESUMO, VISAO_GRAFICOS]

# Identificadores estáveis dos gráficos (usados no session_state)
GRAFICO_EVOLUCAO = "evolucao"
GRAFICO_CATEGORIA = "categoria"
GRAFICO_DISTRIBUICAO = "distribuicao"
GRAFICO_COMPARACAO = "comparacao"

# Chaves de session_state centralizadas
CHAVE_VISOES = "painel_visoes"
CHAVE_GRAFICOS = "painel_graficos"
CHAVE_GRAFICOS_POR_LINHA = "painel_graficos_por_linha"
CHAVE_PREFERENCIAS = "preferencias_dashboard"
CHAVE_ESTATISTICAS_RESUMO = "estatisticas_resumo_dashboard"


# ---------------------------------------------------------------------------
# Estruturas de dados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ContextoPainel:
    """Dados e filtros compartilhados por todos os gráficos."""

    dados: pd.DataFrame
    metrica: str
    valores_metrica: pd.Series
    coluna_temporal: str | None
    coluna_categorica: str | None
    colunas_numericas: list[str]


class EstatisticasResumo(TypedDict):
    total_registros: int
    registros_validos: int
    media_metrica: float | None
    indicadores_numericos: int


@dataclass(frozen=True)
class DefinicaoGrafico:
    """Descreve um gráfico disponível no catálogo."""

    titulo: str
    renderizar: Callable[[ContextoPainel], None]
    minimo_colunas_numericas: int = 1


@dataclass(frozen=True)
class PreferenciasPainel:
    """Escolhas do usuário sobre o que exibir no painel."""

    visoes: tuple[str, ...]
    graficos: tuple[str, ...]
    graficos_por_linha: int

    def exibe_grafico(self, grafico_id: str) -> bool:
        """Indica se o gráfico será exibido com as preferências atuais."""
        return VISAO_GRAFICOS in self.visoes and grafico_id in self.graficos


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def renderizar_painel(dados: pd.DataFrame) -> None:
    """Renderiza o painel personalizável da base de dados."""
    _renderizar_titulo()

    if dados.empty:
        st.warning("A base de dados está vazia.")
        return

    dados = dados.copy()
    dados.columns = dados.columns.astype(str)

    colunas_numericas = _obter_colunas_numericas(dados)
    if not colunas_numericas:
        st.warning("Não foram encontradas colunas numéricas para gerar gráficos.")
        return

    colunas_temporais = _obter_colunas_temporais(dados)
    colunas_categoricas = _obter_colunas_categoricas(
        dados=dados,
        colunas_excluidas=colunas_numericas + colunas_temporais,
    )

    _renderizar_painel_interativo(
        dados=dados,
        colunas_numericas=colunas_numericas,
        colunas_temporais=colunas_temporais,
        colunas_categoricas=colunas_categoricas,
    )


@st.fragment
def _renderizar_painel_interativo(
    dados: pd.DataFrame,
    colunas_numericas: list[str],
    colunas_temporais: list[str],
    colunas_categoricas: list[str],
) -> None:
    """Área interativa do painel.

    Por ser um fragmento, mudanças nos filtros e nas preferências
    reexecutam apenas este bloco, e não a página inteira.
    """
    graficos_disponiveis = _obter_graficos_disponiveis(len(colunas_numericas))

    area_metrica, area_data, area_categoria, area_config = st.columns(
        [1, 1, 2, 1],
        vertical_alignment="bottom",
    )

    # A personalização é lida primeiro porque os filtros dependem dela.
    # Como as colunas já existem, a posição visual não muda.
    with area_config:
        preferencias = _renderizar_personalizacao(graficos_disponiveis)

    metrica, coluna_temporal, coluna_categorica = _renderizar_filtros(
        areas=(area_metrica, area_data, area_categoria),
        colunas_numericas=colunas_numericas,
        colunas_temporais=colunas_temporais,
        colunas_categoricas=colunas_categoricas,
        preferencias=preferencias,
    )
    _registrar_preferencias(
        metrica=metrica,
        coluna_temporal=coluna_temporal,
        coluna_categorica=coluna_categorica,
        preferencias=preferencias,
        estatisticas_resumo=None,
    )

    if not preferencias.visoes:
        st.info("Selecione ao menos uma visão em **Personalizar painel**.")
        return

    valores_metrica = pd.to_numeric(dados[metrica], errors="coerce")
    if valores_metrica.dropna().empty:
        st.warning(f"A coluna '{metrica}' não contém valores numéricos válidos.")
        return

    contexto = ContextoPainel(
        dados=dados,
        metrica=metrica,
        valores_metrica=valores_metrica,
        coluna_temporal=coluna_temporal,
        coluna_categorica=coluna_categorica,
        colunas_numericas=colunas_numericas,
    )

    estatisticas_resumo = (
        _obter_estatisticas_resumo(contexto)
        if VISAO_RESUMO in preferencias.visoes
        else None
    )
    _registrar_preferencias(
        metrica=metrica,
        coluna_temporal=coluna_temporal,
        coluna_categorica=coluna_categorica,
        preferencias=preferencias,
        estatisticas_resumo=estatisticas_resumo,
    )

    # A ordem de exibição é fixa, independente da ordem dos cliques
    if VISAO_RESUMO in preferencias.visoes and estatisticas_resumo is not None:
        _renderizar_resumo(contexto, estatisticas_resumo)

    if VISAO_GRAFICOS in preferencias.visoes:
        _renderizar_graficos(contexto, preferencias, graficos_disponiveis)

    if VISAO_TABELA in preferencias.visoes:
        _renderizar_tabela(contexto.dados)


# ---------------------------------------------------------------------------
# Personalização e filtros
# ---------------------------------------------------------------------------

def _renderizar_personalizacao(
    graficos_disponiveis: dict[str, DefinicaoGrafico],
) -> PreferenciasPainel:
    """Renderiza as opções de personalização e retorna as escolhas do usuário."""
    _sincronizar_selecao_graficos(list(graficos_disponiveis))

    with st.popover("Personalizar painel", icon=":material/tune:"):
        visoes = st.pills(
            "Visões",
            options=VISOES,
            default=VISOES_PADRAO,
            selection_mode="multi",
            key=CHAVE_VISOES,
        )

        # Sem `default`: o valor inicial vem do session_state (ver sincronização)
        graficos = st.pills(
            "Gráficos",
            options=list(graficos_disponiveis),
            format_func=lambda grafico_id: graficos_disponiveis[grafico_id].titulo,
            selection_mode="multi",
            key=CHAVE_GRAFICOS,
            disabled=VISAO_GRAFICOS not in (visoes or []),
        )

        graficos_por_linha = st.segmented_control(
            "Gráficos por linha",
            options=[1, 2],
            default=2,
            key=CHAVE_GRAFICOS_POR_LINHA,
        )

    # Mantém a ordem do catálogo, e não a ordem em que o usuário clicou
    graficos_ordenados = tuple(
        grafico_id for grafico_id in graficos_disponiveis if grafico_id in (graficos or [])
    )

    return PreferenciasPainel(
        visoes=tuple(visoes or []),
        graficos=graficos_ordenados,
        # segmented_control retorna None se o usuário desmarcar a opção atual
        graficos_por_linha=graficos_por_linha or 2,
    )


def _sincronizar_selecao_graficos(opcoes_validas: list[str]) -> None:
    """Inicializa a seleção de gráficos e remove opções indisponíveis.

    Necessário quando o usuário troca de arquivo: a nova base pode não
    suportar um gráfico que estava selecionado. Precisa rodar antes da
    criação do widget.
    """
    selecao_atual = st.session_state.get(CHAVE_GRAFICOS)

    if selecao_atual is None:
        st.session_state[CHAVE_GRAFICOS] = list(opcoes_validas)
        return

    st.session_state[CHAVE_GRAFICOS] = [
        grafico_id for grafico_id in selecao_atual if grafico_id in opcoes_validas
    ]


def _renderizar_filtros(
    areas: tuple[DeltaGenerator, DeltaGenerator, DeltaGenerator],
    colunas_numericas: list[str],
    colunas_temporais: list[str],
    colunas_categoricas: list[str],
    preferencias: PreferenciasPainel,
) -> tuple[str, str | None, str | None]:
    """Renderiza os filtros, desativando os que não afetam o que está na tela."""
    area_metrica, area_data, area_categoria = areas

    metrica = area_metrica.selectbox(
        "Indicador principal",
        options=colunas_numericas,
        key="painel_metrica",
    )

    coluna_temporal = area_data.selectbox(
        "Eixo temporal",
        options=[None, *colunas_temporais],
        format_func=lambda valor: valor or "Ordem dos registros",
        key="painel_eixo_temporal",
        disabled=not preferencias.exibe_grafico(GRAFICO_EVOLUCAO),
    )

    coluna_categorica = area_categoria.selectbox(
        "Agrupar por categoria",
        options=[None, *colunas_categoricas],
        format_func=lambda valor: valor or "Sem agrupamento",
        key="painel_categoria",
        disabled=not preferencias.exibe_grafico(GRAFICO_CATEGORIA),
    )

    return metrica, coluna_temporal, coluna_categorica


# ---------------------------------------------------------------------------
# Visões
# ---------------------------------------------------------------------------

def _obter_estatisticas_resumo(
    contexto: ContextoPainel,
) -> EstatisticasResumo:
    media = contexto.valores_metrica.mean()
    return {
        "total_registros": len(contexto.dados),
        "registros_validos": int(contexto.valores_metrica.notna().sum()),
        "media_metrica": None if pd.isna(media) else float(media),
        "indicadores_numericos": len(contexto.colunas_numericas),
    }


def _registrar_preferencias(
    metrica: str,
    coluna_temporal: str | None,
    coluna_categorica: str | None,
    preferencias: PreferenciasPainel,
    estatisticas_resumo: EstatisticasResumo | None,
) -> None:
    st.session_state[CHAVE_ESTATISTICAS_RESUMO] = estatisticas_resumo
    st.session_state[CHAVE_PREFERENCIAS] = {
        "metrica_principal": metrica,
        "eixo_temporal": coluna_temporal,
        "coluna_categorica": coluna_categorica,
        "visoes": list(preferencias.visoes),
        "graficos": list(preferencias.graficos),
        "graficos_por_linha": preferencias.graficos_por_linha,
        "estatisticas_resumo": estatisticas_resumo,
    }


def _renderizar_resumo(
    contexto: ContextoPainel,
    estatisticas: EstatisticasResumo,
) -> None:
    """Renderiza os indicadores resumidos da base."""
    cartoes = st.columns(4)

    cartoes[0].metric(
        "Registros",
        _formatar_inteiro(estatisticas["total_registros"]),
    )
    cartoes[1].metric(
        "Registros válidos",
        _formatar_inteiro(estatisticas["registros_validos"]),
    )
    cartoes[2].metric(
        f"Média de {contexto.metrica}",
        _formatar_numero(estatisticas["media_metrica"]),
    )
    cartoes[3].metric(
        "Indicadores numéricos",
        estatisticas["indicadores_numericos"],
    )


def _renderizar_graficos(
    contexto: ContextoPainel,
    preferencias: PreferenciasPainel,
    graficos_disponiveis: dict[str, DefinicaoGrafico],
) -> None:
    """Renderiza os gráficos selecionados em uma grade configurável."""
    if not preferencias.graficos:
        st.info("Nenhum gráfico selecionado. Escolha os gráficos em **Personalizar painel**.")
        return

    definicoes = [graficos_disponiveis[grafico_id] for grafico_id in preferencias.graficos]
    por_linha = preferencias.graficos_por_linha

    # Monta a grade linha a linha, com `por_linha` gráficos em cada uma
    for inicio in range(0, len(definicoes), por_linha):
        colunas = st.columns(por_linha, gap="large")
        for coluna, definicao in zip(colunas, definicoes[inicio:inicio + por_linha]):
            with coluna, st.container(border=True):
                definicao.renderizar(contexto)


def _renderizar_tabela(dados: pd.DataFrame) -> None:
    """Renderiza a tabela com os dados da base."""
    st.markdown("##### Dados da base")
    st.dataframe(dados, width="stretch", hide_index=True, height=ALTURA_GRAFICO)


# ---------------------------------------------------------------------------
# Gráficos (todos com a mesma assinatura: recebem ContextoPainel)
# ---------------------------------------------------------------------------

def _renderizar_grafico_evolucao(contexto: ContextoPainel) -> None:
    """Renderiza a evolução temporal ou sequencial do indicador."""
    metrica = contexto.metrica
    coluna_temporal = contexto.coluna_temporal
    st.markdown(f"##### Evolução de {metrica}")

    if coluna_temporal:
        dados_grafico = contexto.dados[[coluna_temporal, metrica]].copy()
        dados_grafico[metrica] = pd.to_numeric(dados_grafico[metrica], errors="coerce")
        dados_grafico[coluna_temporal] = pd.to_datetime(
            dados_grafico[coluna_temporal], errors="coerce"
        )

        dados_grafico = (
            dados_grafico
            .dropna()
            .groupby(coluna_temporal, as_index=False)[metrica]
            .mean()
            .sort_values(coluna_temporal)
            .tail(LIMITE_REGISTROS_GRAFICO)  # tail: mantém os períodos mais recentes
        )

        if dados_grafico.empty:
            st.info("Não há dados suficientes para gerar a evolução temporal.")
            return

        st.line_chart(
            dados_grafico, x=coluna_temporal, y=metrica,
            height=ALTURA_GRAFICO, width="stretch",
        )
        return

    dados_grafico = (
        contexto.valores_metrica
        .dropna()
        .head(LIMITE_REGISTROS_GRAFICO)
        .reset_index(drop=True)
        .to_frame(name=metrica)
    )
    dados_grafico["Registro"] = dados_grafico.index + 1

    st.line_chart(
        dados_grafico, x="Registro", y=metrica,
        height=ALTURA_GRAFICO, width="stretch",
    )


def _renderizar_grafico_categoria(contexto: ContextoPainel) -> None:
    """Renderiza o indicador agrupado por categoria."""
    metrica = contexto.metrica
    coluna_categorica = contexto.coluna_categorica
    st.markdown(f"##### {metrica} por grupo")

    if not coluna_categorica:
        # rename_axis + reset_index evita depender do nome "index"
        dados_grafico = (
            contexto.valores_metrica
            .dropna()
            .nlargest(LIMITE_CATEGORIAS)
            .rename_axis("Registro")
            .reset_index()
        )

        st.bar_chart(
            dados_grafico, x="Registro", y=metrica,
            height=ALTURA_GRAFICO, width="stretch",
        )
        return

    dados_grafico = contexto.dados[[coluna_categorica, metrica]].copy()
    dados_grafico[metrica] = pd.to_numeric(dados_grafico[metrica], errors="coerce")
    dados_grafico[coluna_categorica] = (
        dados_grafico[coluna_categorica].fillna("Sem categoria").astype(str)
    )

    dados_grafico = (
        dados_grafico
        .dropna(subset=[metrica])
        .groupby(coluna_categorica, as_index=False)[metrica]
        .mean()
        .nlargest(LIMITE_CATEGORIAS, metrica)
    )

    if dados_grafico.empty:
        st.info("Não há dados suficientes para gerar o agrupamento.")
        return

    st.bar_chart(
        dados_grafico, x=coluna_categorica, y=metrica,
        height=ALTURA_GRAFICO, width="stretch",
    )


def _renderizar_grafico_distribuicao(contexto: ContextoPainel) -> None:
    """Renderiza a distribuição dos valores do indicador."""
    st.markdown(f"##### Distribuição de {contexto.metrica}")

    # np.nan mantém a série como float; pd.NA a convertia para object
    valores_validos = (
        contexto.valores_metrica.replace([np.inf, -np.inf], np.nan).dropna()
    )

    if valores_validos.empty:
        st.info("Não há dados suficientes para gerar a distribuição.")
        return

    quantidade_valores = valores_validos.nunique()

    if quantidade_valores == 1:
        st.metric("Valor", _formatar_numero(valores_validos.iloc[0]))
        return

    distribuicao = (
        pd.cut(
            valores_validos,
            bins=min(QUANTIDADE_MAXIMA_FAIXAS, quantidade_valores),
            duplicates="drop",
        )
        .value_counts(sort=False)
        .rename_axis("Faixa")
        .reset_index(name="Registros")
    )
    distribuicao["Faixa"] = distribuicao["Faixa"].astype(str)

    st.bar_chart(
        distribuicao, x="Faixa", y="Registros",
        height=ALTURA_GRAFICO, width="stretch",
    )


def _renderizar_grafico_comparacao(contexto: ContextoPainel) -> None:
    """Renderiza a relação entre dois indicadores numéricos."""
    metrica = contexto.metrica
    metricas_disponiveis = [c for c in contexto.colunas_numericas if c != metrica]

    # Proteção extra: o catálogo já esconde este gráfico com menos de 2 colunas
    if not metricas_disponiveis:
        st.markdown(f"##### Comparação de {metrica}")
        st.info("É necessário outro indicador numérico para realizar comparações.")
        return

    metrica_comparacao = st.selectbox(
        "Comparar com",
        options=metricas_disponiveis,
        key="painel_metrica_comparacao",
    )

    st.markdown(f"##### Relação entre {metrica} e {metrica_comparacao}")

    dados_grafico = contexto.dados[[metrica, metrica_comparacao]].apply(
        pd.to_numeric, errors="coerce"
    )
    dados_grafico = (
        dados_grafico
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .head(LIMITE_REGISTROS_GRAFICO)
    )

    if dados_grafico.empty:
        st.info("Não há dados suficientes para comparar os indicadores.")
        return

    st.scatter_chart(
        dados_grafico, x=metrica, y=metrica_comparacao,
        height=ALTURA_GRAFICO, width="stretch",
    )


# ---------------------------------------------------------------------------
# Catálogo (definido após as funções que referencia)
# ---------------------------------------------------------------------------

CATALOGO_GRAFICOS: dict[str, DefinicaoGrafico] = {
    GRAFICO_EVOLUCAO: DefinicaoGrafico("Evolução", _renderizar_grafico_evolucao),
    GRAFICO_CATEGORIA: DefinicaoGrafico("Por grupo", _renderizar_grafico_categoria),
    GRAFICO_DISTRIBUICAO: DefinicaoGrafico("Distribuição", _renderizar_grafico_distribuicao),
    GRAFICO_COMPARACAO: DefinicaoGrafico(
        "Comparação", _renderizar_grafico_comparacao, minimo_colunas_numericas=2
    ),
}


def _obter_graficos_disponiveis(quantidade_numericas: int) -> dict[str, DefinicaoGrafico]:
    """Retorna apenas os gráficos que a base atual consegue alimentar."""
    return {
        grafico_id: definicao
        for grafico_id, definicao in CATALOGO_GRAFICOS.items()
        if quantidade_numericas >= definicao.minimo_colunas_numericas
    }


# ---------------------------------------------------------------------------
# Detecção de colunas e utilitários
# ---------------------------------------------------------------------------

def _obter_colunas_numericas(dados: pd.DataFrame) -> list:
    """Retorna as colunas numéricas disponíveis."""
    return dados.select_dtypes(include="number").columns.tolist()


def _obter_colunas_temporais(dados: pd.DataFrame) -> list:
    """Retorna as colunas que possuem tipo temporal."""
    return dados.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()


def _obter_colunas_categoricas(
    dados: pd.DataFrame,
    colunas_excluidas: list[str],
) -> list:
    """Retorna as colunas categóricas disponíveis, excluindo as fornecidas."""
    return [coluna for coluna in dados.columns if coluna not in colunas_excluidas]


def _renderizar_titulo() -> None:
    """Renderiza o título da seção."""
    st.markdown('<p class="section-heading">Dashboard dos dados</p>', unsafe_allow_html=True)


def _formatar_numero(valor: float | int | None) -> str:
    """Formata um número utilizando o padrão brasileiro."""
    if pd.isna(valor):
        return "-"
    return f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _formatar_inteiro(valor: int) -> str:
    """Formata um número inteiro utilizando separador de milhar."""
    return f"{valor:,}".replace(",", ".")