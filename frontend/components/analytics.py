from typing import Any

import pandas as pd
import streamlit as st

from src.prompts.prompt import criar_prompt_diagnostico
from src.services.api.service_gemini import (GeminiServiceError, analise_indicadores_gemini,)


def renderizar_secao_analise(dados: pd.DataFrame | None, arquivo_enviado: bool) -> None:
    st.markdown("#### Análise com IA")

    if not _renderizar_botao_analise():
        diagnostico = st.session_state.get("diagnostico")
        if diagnostico:
            _renderizar_diagnostico(diagnostico)
        else:
            _renderizar_estado_inicial()
        return

    if not _validar_dados(dados=dados, arquivo_enviado=arquivo_enviado):
        return
    
    analise = st.session_state.get("analise")
    if not isinstance(analise, dict):
        st.error("Não foi possível gerar o diagnóstico porque a análise não está disponível.")
        return

    try:
        diagnostico = _gerar_diagnostico(analise)
    except (GeminiServiceError, ValueError) as erro:
        st.error(f"Não foi possível gerar o diagnóstico: {erro}")
        return

    st.session_state["diagnostico"] = diagnostico
    _renderizar_diagnostico(diagnostico)


def _renderizar_botao_analise() -> bool:
    """Renderiza o botão responsável por iniciar a análise."""
    return st.button(
            "Analisar indicadores identificados com IA",
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


def _gerar_diagnostico(analise: dict[str, Any]) -> str:
    """Gera o diagnóstico com base na análise dos indicadores."""
    prompt = criar_prompt_diagnostico(analise)
    return analise_indicadores_gemini(prompt)

def _renderizar_diagnostico(diagnostico: str) -> None:
    """Renderiza o diagnóstico gerado pela IA."""
    st.markdown("#### Diagnóstico Gemini")
    st.markdown(diagnostico)


def _renderizar_estado_inicial() -> None:
    """Renderiza a mensagem inicial da seção de análise."""
    st.info("Após, você pode clicar no botão para iniciar a análise os resultados aparecerão aqui.")