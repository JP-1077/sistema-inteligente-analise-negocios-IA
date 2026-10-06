from typing import Any

import pandas as pd
import streamlit as st

from prompts.prompt import criar_prompt_diagnostico
from services.service_api_gemini import ServiceApiGemini
from services.service_analytics import KPIanaliser


def renderizar_secao_analise(dados: pd.DataFrame | None, arquivo_enviado: bool) -> None:
    st.subheader("Resulta da análise")

    if not _renderizar_botao_analise():
        _renderizar_estado_inicial()
        return

    if not _validar_dados(dados=dados, arquivo_enviado=arquivo_enviado):
        return
    
    try:
        analise = KPIanaliser.analise(dados)
    except ValueError as erro:
        st.error(str(erro))
        return

    _renderizar_indicadores(analise)

    try:
        diagnostico = _gerar_diagnostico(analise)
    except Exception:
        st.error("Não foi possível gerar o diagnóstico neste momento.")
        return

    _renderizar_diagnostico(diagnostico)



def _renderizar_botao_analise() -> bool:
    """Renderiza o botão responsável por iniciar a análise."""
    coluna_botao, _ = st.columns([1, 3])

    with coluna_botao:
        return st.button(
            "Analisar indicadores com IA",
            type="primary",
            width="stretch",
        )


def _validar_dados(dados: pd.DataFrame | None, arquivo_enviado: bool) -> bool:

    """Valida os dados necessários para iniciar a análise."""

    if not arquivo_enviado:
        st.warning("Envie um arquivo CSV ou Excel antes de iniciar a análise.")
        return False

    if dados is None:
        st.warning("Corrija o arquivo enviado antes de iniciar a análise.")
        return False

    if dados.empty:
        st.warning("O arquivo enviado não contém dados para análise.")
        return False

    return True


def _renderizar_indicadores(analise: dict[str, Any]) -> None:
    """Renderiza os indicadores identificados na análise."""
    indicadores = [
        {
            "KPI": nome,
            "Valor anterior": valores["previous_value"],
            "Valor atual": valores["current_value"],
            "Variação (%)": valores["variation"],
            "Status": valores["status"],
            "Tendência": valores["trend"],
        }
        for nome, valores in analise["kpis"].items()
    ]

    st.markdown("#### Indicadores identificados")

    st.dataframe(
        indicadores,
        width="stretch",
        hide_index=True,
    )


def _gerar_diagnostico(analise: dict[str, Any]) -> str:
    """Gera o diagnóstico com base na análise dos indicadores."""
    prompt = criar_prompt_diagnostico(analise)
    diagnostico = ServiceApiGemini.gerar_resposta(prompt)
    return diagnostico

def _renderizar_diagnostico(diagnostico: str) -> None:
    """Renderiza o diagnóstico gerado pela IA."""
    st.markdown("#### Diagnóstico Gemini")
    st.markdown(diagnostico)


def _renderizar_estado_inicial() -> None:
    """Renderiza a mensagem inicial da seção de análise."""
    st.info("Os resultados aparecerão aqui depois que você enviar um arquivo e clicar em **Analisar indicadores com IA**.")