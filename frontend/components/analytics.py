from typing import Any

import pandas as pd
import streamlit as st

from src.prompts.prompt import criar_prompt_diagnostico
from src.services.api.service_gemini import (GeminiServiceError, analise_indicadores_gemini,)
from src.services.service_analytics_ import service_analytics


def renderizar_secao_analise(dados: pd.DataFrame | None, arquivo_enviado: bool) -> None:
    st.subheader("Resultado da análise")

    if not _renderizar_botao_analise():
        _renderizar_estado_inicial()
        return

    if not _validar_dados(dados=dados, arquivo_enviado=arquivo_enviado):
        return
    
    try:
        analise = service_analytics(dados)
    except ValueError as erro:
        st.error(str(erro))
        return

    _renderizar_indicadores(analise)

    try:
        diagnostico = _gerar_diagnostico(analise)
    except (GeminiServiceError, ValueError) as erro:
        st.error(f"Não foi possível gerar o diagnóstico: {erro}")
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
    estatisticas = analise["estatisticas"]
    resultados_temporais = analise["tendencias"]["resultados"]
    anomalias = analise["anomalias"]
    indicadores = []

    for metrica in analise["metricas_identificadas"]:
        nome = metrica["nome"]
        estatistica = estatisticas.get(nome, {})
        tendencia = resultados_temporais.get(nome, {})
        anomalia = anomalias.get(nome)

        indicadores.append(
            {
                "Indicador": nome,
                "Média": estatistica.get("media"),
                "Mínimo": estatistica.get("minimo"),
                "Máximo": estatistica.get("maximo"),
                "Valor anterior": tendencia.get("valor_anterior"),
                "Valor atual": tendencia.get("valor_atual"),
                "Variação (%)": tendencia.get("variacao_percentual"),
                "Tendência": tendencia.get("direcao"),
                "Anomalias": (
                    anomalia["quantidade_anomalias"]
                    if anomalia is not None
                    else "Não avaliado"
                ),
            }
        )

    st.markdown("#### Indicadores identificados")

    st.dataframe(
        indicadores,
        width="stretch",
        hide_index=True,
    )


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
    st.info("Os resultados aparecerão aqui depois que você enviar um arquivo e clicar em **Analisar indicadores com IA**.")