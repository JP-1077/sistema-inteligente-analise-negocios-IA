from typing import Any
import pandas as pd
import streamlit as st

from src.services.service_analytics_ import service_analytics

@st.cache_data(show_spinner="Identificando indicadores...")
def _executar_analise(dados: pd.DataFrame) -> dict[str, Any]:
    try:
        return service_analytics.analisar_dados(dados)
    except Exception as e:
        st.error(f"Erro ao executar análise: {e}")
        return {}


def renderizar_secao_indicadores(dados: pd.DataFrame | None, arquivo_enviado: bool,) -> dict[str, Any] | None:
    
        st.markdown("### Indicadores identificados")

        dados_validos = _obter_dados_validos(dados, arquivo_enviado)
        if dados_validos is None:
            return None
    
        try: 
            analise = _executar_analise(dados_validos)
        except ValueError as erro:
            st.error(str(erro))
            return None
        
        _renderizar_tabela_indicadores(analise)
        return analise

def _obter_dados_validos(dados: pd.DataFrame | None, arquivo_enviado: bool) -> pd.DataFrame | None:

    if dados is None:
        st.info("Nenhum arquivo disponibilizado. Envie um arquivo no formato .csv ou .xlsx para identificar os indicadores.")
        return None

    if dados.empty:
        st.info("O arquivo enviado está vazio. Por favor, envie um arquivo com dados válidos.")
        return None

def _renderizar_tabela_indicadores(analise: dict[str, Any]) -> None:
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
                "Valor atual": tendencia.get("valor_atual"),
                "Variação (%)": tendencia.get("variacao_percentual"),
                "Tendência": tendencia.get("direcao"),
                "Anomalias": (anomalia["quantidade_anomalias"] if anomalia is not None else "Não avaliado"),
            }
        )

    if not indicadores:
        st.info("Nenhum indicador numérico foi identificado na base enviada.")
        return

    st.dataframe(indicadores, width="stretch", hide_index=True)