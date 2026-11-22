from typing import Any

import pandas as pd
import streamlit as st

from src.services.service_analytics_ import service_analytics


@st.cache_data(show_spinner="Identificando indicadores...")
def _executar_analise(dados: pd.DataFrame) -> dict[str, Any]:
    return service_analytics(dados)


def renderizar_secao_indicadores(
    dados: pd.DataFrame | None,
    arquivo_enviado: bool,
) -> dict[str, Any] | None:
    st.markdown("### Indicadores identificados")

    dados_validos = _obter_dados_validos(dados)
    if dados_validos is None:
        return None

    try:
        analise = _executar_analise(dados_validos)
    except (TypeError, ValueError) as erro:
        st.error(f"Erro ao identificar KPIs: {erro}")
        return None

    _renderizar_tabela_indicadores(analise)
    return analise


def _obter_dados_validos(
    dados: pd.DataFrame | None,
) -> pd.DataFrame | None:
    if dados is None:
        st.info(
            "Nenhum arquivo disponibilizado. Envie um arquivo no formato "
            ".csv ou .xlsx para identificar os indicadores."
        )
        return None

    if dados.empty:
        st.info("O arquivo enviado está vazio. Envie uma base com dados.")
        return None

    return dados


def _renderizar_tabela_indicadores(analise: dict[str, Any]) -> None:
    indicadores = [
        {"KPI": metrica["nome"]}
        for metrica in analise["metricas_identificadas"]
    ]

    if not indicadores:
        st.info("Nenhum indicador numérico foi identificado na base enviada.")
        return

    st.dataframe(indicadores, width="stretch", hide_index=True)