"""Componente responsável pela renderização do painel de dados."""

import pandas as pd
import streamlit as st


LIMITE_REGISTROS_GRAFICO = 1_000
LIMITE_CATEGORIAS = 15
ALTURA_GRAFICO = 340
QUANTIDADE_MAXIMA_FAIXAS = 12


def renderizar_painel(dados: pd.DataFrame) -> None:
    """Renderiza os principais indicadores e gráficos da base de dados."""
    _renderizar_titulo()

    if dados.empty:
        st.warning("A base de dados está vazia.")
        return

    dados = dados.copy()
    dados.columns = dados.columns.astype(str)

    colunas_numericas = _obter_colunas_numericas(dados)

    if not colunas_numericas:
        st.warning(
            "Não foram encontradas colunas numéricas para gerar gráficos."
        )
        return

    colunas_temporais = _obter_colunas_temporais(dados)

    colunas_categoricas = _obter_colunas_categoricas(
        dados=dados,
        colunas_excluidas=colunas_numericas + colunas_temporais,
    )

    metrica, coluna_temporal, coluna_categorica = _renderizar_filtros(
        colunas_numericas=colunas_numericas,
        colunas_temporais=colunas_temporais,
        colunas_categoricas=colunas_categoricas,
    )

    valores_metrica = pd.to_numeric(
        dados[metrica],
        errors="coerce",
    )

    if valores_metrica.dropna().empty:
        st.warning(
            f"A coluna '{metrica}' não contém valores numéricos válidos."
        )
        return

    _renderizar_resumo(
        dados=dados,
        metrica=metrica,
        valores_metrica=valores_metrica,
        colunas_numericas=colunas_numericas,
    )

    _renderizar_graficos(
        dados=dados,
        metrica=metrica,
        valores_metrica=valores_metrica,
        coluna_temporal=coluna_temporal,
        coluna_categorica=coluna_categorica,
        colunas_numericas=colunas_numericas,
    )


def _obter_colunas_numericas(dados: pd.DataFrame) -> list:
    """Retorna as colunas numéricas disponíveis."""
    return dados.select_dtypes(
        include="number",
    ).columns.tolist()


def _obter_colunas_temporais(dados: pd.DataFrame) -> list:
    """Retorna as colunas que possuem tipo temporal."""
    return dados.select_dtypes(
        include=["datetime", "datetimetz"],
    ).columns.tolist()


def _obter_colunas_categoricas(
    dados: pd.DataFrame,
    colunas_excluidas: list[str],
) -> list[str]:
    """Retorna as colunas disponíveis para agrupamento."""
    return [
        coluna
        for coluna in dados.columns
        if coluna not in colunas_excluidas
    ]


def _renderizar_filtros(
    colunas_numericas: list[str],
    colunas_temporais: list[str],
    colunas_categoricas: list[str],
) -> tuple[str, str | None, str | None]:
    """Renderiza os filtros principais do painel."""
    coluna_metrica, coluna_data, coluna_categoria = st.columns(
        [1, 1, 2]
    )

    metrica = coluna_metrica.selectbox(
        "Indicador principal",
        options=colunas_numericas,
        key="painel_metrica",
    )

    coluna_temporal = coluna_data.selectbox(
        "Eixo temporal",
        options=[None, *colunas_temporais],
        format_func=lambda valor: valor or "Ordem dos registros",
        key="painel_eixo_temporal",
    )

    coluna_categorica = coluna_categoria.selectbox(
        "Agrupar por categoria",
        options=[None, *colunas_categoricas],
        format_func=lambda valor: valor or "Sem agrupamento",
        key="painel_categoria",
    )

    return metrica, coluna_temporal, coluna_categorica


def _renderizar_resumo(
    dados: pd.DataFrame,
    metrica: str,
    valores_metrica: pd.Series,
    colunas_numericas: list[str],
) -> None:
    """Renderiza os indicadores resumidos da base."""
    cartoes = st.columns(4)

    cartoes[0].metric(
        "Registros",
        _formatar_inteiro(len(dados)),
    )

    cartoes[1].metric(
        "Registros válidos",
        _formatar_inteiro(valores_metrica.notna().sum()),
    )

    cartoes[2].metric(
        f"Média de {metrica}",
        _formatar_numero(valores_metrica.mean()),
    )

    cartoes[3].metric(
        "Indicadores numéricos",
        len(colunas_numericas),
    )


def _renderizar_graficos(
    dados: pd.DataFrame,
    metrica: str,
    valores_metrica: pd.Series,
    coluna_temporal: str | None,
    coluna_categorica: str | None,
    colunas_numericas: list[str],
) -> None:
    """Organiza e renderiza os gráficos do painel."""
    primeira_coluna, segunda_coluna = st.columns(
        2,
        gap="large",
    )

    with primeira_coluna:
        _renderizar_grafico_evolucao(
            dados=dados,
            metrica=metrica,
            coluna_temporal=coluna_temporal,
        )

    with segunda_coluna:
        _renderizar_grafico_categoria(
            dados=dados,
            metrica=metrica,
            coluna_categorica=coluna_categorica,
        )

    terceira_coluna, quarta_coluna = st.columns(
        2,
        gap="large",
    )

    with terceira_coluna:
        _renderizar_grafico_distribuicao(
            metrica=metrica,
            valores_metrica=valores_metrica,
        )

    with quarta_coluna:
        _renderizar_grafico_comparacao(
            dados=dados,
            metrica=metrica,
            colunas_numericas=colunas_numericas,
        )


def _renderizar_grafico_evolucao(
    dados: pd.DataFrame,
    metrica: str,
    coluna_temporal: str | None,
) -> None:
    """Renderiza a evolução temporal ou sequencial do indicador."""
    st.markdown(f"##### Evolução de {metrica}")

    if coluna_temporal:
        dados_grafico = dados[
            [coluna_temporal, metrica]
        ].copy()

        dados_grafico[metrica] = pd.to_numeric(
            dados_grafico[metrica],
            errors="coerce",
        )

        dados_grafico[coluna_temporal] = pd.to_datetime(
            dados_grafico[coluna_temporal],
            errors="coerce",
        )

        dados_grafico = (
            dados_grafico
            .dropna()
            .groupby(coluna_temporal, as_index=False)[metrica]
            .mean()
            .sort_values(coluna_temporal)
            .head(LIMITE_REGISTROS_GRAFICO)
        )

        if dados_grafico.empty:
            st.info(
                "Não há dados suficientes para gerar a evolução temporal."
            )
            return

        st.line_chart(
            dados_grafico,
            x=coluna_temporal,
            y=metrica,
            height=ALTURA_GRAFICO,
            width="stretch",
        )
        return

    dados_grafico = dados[[metrica]].copy()

    dados_grafico[metrica] = pd.to_numeric(
        dados_grafico[metrica],
        errors="coerce",
    )

    dados_grafico = (
        dados_grafico
        .dropna()
        .head(LIMITE_REGISTROS_GRAFICO)
        .reset_index(drop=True)
    )

    dados_grafico["Registro"] = dados_grafico.index + 1

    st.line_chart(
        dados_grafico,
        x="Registro",
        y=metrica,
        height=ALTURA_GRAFICO,
        width="stretch",
    )


def _renderizar_grafico_categoria(
    dados: pd.DataFrame,
    metrica: str,
    coluna_categorica: str | None,
) -> None:
    """Renderiza o indicador agrupado por categoria."""
    st.markdown(f"##### {metrica} por grupo")

    if not coluna_categorica:
        dados_grafico = dados[[metrica]].copy()

        dados_grafico[metrica] = pd.to_numeric(
            dados_grafico[metrica],
            errors="coerce",
        )

        dados_grafico = (
            dados_grafico
            .dropna()
            .nlargest(LIMITE_CATEGORIAS, metrica)
            .reset_index()
            .rename(columns={"index": "Registro"})
        )

        st.bar_chart(
            dados_grafico,
            x="Registro",
            y=metrica,
            height=ALTURA_GRAFICO,
            width="stretch",
        )
        return

    dados_grafico = dados[
        [coluna_categorica, metrica]
    ].copy()

    dados_grafico[metrica] = pd.to_numeric(
        dados_grafico[metrica],
        errors="coerce",
    )

    dados_grafico[coluna_categorica] = (
        dados_grafico[coluna_categorica]
        .fillna("Sem categoria")
        .astype(str)
    )

    dados_grafico = (
        dados_grafico
        .dropna(subset=[metrica])
        .groupby(coluna_categorica, as_index=False)[metrica]
        .mean()
        .nlargest(LIMITE_CATEGORIAS, metrica)
    )

    if dados_grafico.empty:
        st.info(
            "Não há dados suficientes para gerar o agrupamento."
        )
        return

    st.bar_chart(
        dados_grafico,
        x=coluna_categorica,
        y=metrica,
        height=ALTURA_GRAFICO,
        width="stretch",
    )


def _renderizar_grafico_distribuicao(
    metrica: str,
    valores_metrica: pd.Series,
) -> None:
    """Renderiza a distribuição dos valores do indicador."""
    st.markdown(f"##### Distribuição de {metrica}")

    valores_validos = (
        valores_metrica
        .replace([float("inf"), float("-inf")], pd.NA)
        .dropna()
    )

    if valores_validos.empty:
        st.info(
            "Não há dados suficientes para gerar a distribuição."
        )
        return

    quantidade_valores = valores_validos.nunique()

    if quantidade_valores == 1:
        st.metric(
            "Valor",
            _formatar_numero(valores_validos.iloc[0]),
        )
        return

    quantidade_faixas = min(
        QUANTIDADE_MAXIMA_FAIXAS,
        quantidade_valores,
    )

    distribuicao = (
        pd.cut(
            valores_validos,
            bins=quantidade_faixas,
            duplicates="drop",
        )
        .value_counts(sort=False)
        .rename_axis("Faixa")
        .reset_index(name="Registros")
    )

    distribuicao["Faixa"] = distribuicao["Faixa"].astype(str)

    st.bar_chart(
        distribuicao,
        x="Faixa",
        y="Registros",
        height=ALTURA_GRAFICO,
        width="stretch",
    )


def _renderizar_grafico_comparacao(
    dados: pd.DataFrame,
    metrica: str,
    colunas_numericas: list[str],
) -> None:
    """Renderiza a relação entre dois indicadores numéricos."""
    metricas_disponiveis = [
        coluna
        for coluna in colunas_numericas
        if coluna != metrica
    ]

    if not metricas_disponiveis:
        st.markdown(f"##### Comparação de {metrica}")
        st.info(
            "É necessário outro indicador numérico para realizar comparações."
        )
        return

    metrica_comparacao = st.selectbox(
        "Comparar com",
        options=metricas_disponiveis,
        key="painel_metrica_comparacao",
    )

    st.markdown(
        f"##### Relação entre {metrica} e {metrica_comparacao}"
    )

    dados_grafico = dados[
        [metrica, metrica_comparacao]
    ].copy()

    dados_grafico[metrica] = pd.to_numeric(
        dados_grafico[metrica],
        errors="coerce",
    )

    dados_grafico[metrica_comparacao] = pd.to_numeric(
        dados_grafico[metrica_comparacao],
        errors="coerce",
    )

    dados_grafico = (
        dados_grafico
        .replace([float("inf"), float("-inf")], pd.NA)
        .dropna()
        .head(LIMITE_REGISTROS_GRAFICO)
    )

    if dados_grafico.empty:
        st.info(
            "Não há dados suficientes para comparar os indicadores."
        )
        return

    st.scatter_chart(
        dados_grafico,
        x=metrica,
        y=metrica_comparacao,
        height=ALTURA_GRAFICO,
        width="stretch",
    )


def _renderizar_titulo() -> None:
    """Renderiza o título da seção."""
    st.markdown(
        '<p class="section-heading">Dashboard dos dados</p>',
        unsafe_allow_html=True,
    )


def _formatar_numero(valor: float | int) -> str:
    """Formata um número utilizando o padrão brasileiro."""
    if pd.isna(valor):
        return "-"

    return (
        f"{valor:,.2f}"
        .replace(",", "_")
        .replace(".", ",")
        .replace("_", ".")
    )


def _formatar_inteiro(valor: int) -> str:
    """Formata um número inteiro utilizando separador de milhar."""
    return f"{valor:,}".replace(",", ".")