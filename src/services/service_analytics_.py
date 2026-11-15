"""
=======================================================================
            SERVICE ANALYTICS -> ANÁLISE DE DADOS E KPIs
=======================================================================


Descrição:
Service responsável por orquestrar as análises realizadas sobre um dataframe.


Responsabilidades:
Gerar o perfil dos dados, identificar métricas, calcular estatísticas descritivas e análises temporais e detectar anomalias.

"""

import pandas as pd

from .analyzers.estrutura_dados import estrutura_dados
from .analyzers.metricas import identificacao_metricas
from .analyzers.calculo_metricas import calculo_metricas
from .analyzers.metricas_temporais import calculo_anaise_temporais
from .analyzers.anomalias import calculo_anomalias


def service_analytics( df: pd.DataFrame, date_column: str | None = None,) -> dict:
    """
    Função responsável por executar as análises disponíveis para um dataframe.

    Entradas:
        * Dataframe a ser analisado
        * Nome da coluna temporal (opcional; quando omitido, tenta identificar uma coluna temporal)

    Saídas:
        Retorna um dicionário com resumo, perfil dos dados, métricas identificadas,
        estatísticas descritivas, tendências temporais e anomalias.

    Exceções:
        TypeError: quando a entrada não é um pandas.DataFrame.
        ValueError: quando o dataframe não possui registros ou colunas.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("A entrada deve ser um DataFrame.")

    if df.empty:
        raise ValueError("Não existem registros para analisar.")

    if len(df.columns) == 0:
        raise ValueError("A base não possui colunas.")

    profile = estrutura_dados(df)
    metrics = identificacao_metricas(df)
    descriptive = calculo_metricas(df)
    trends = calculo_anaise_temporais(df, date_column=date_column)
    anomalies = calculo_anomalias(df)

    return {
        "resumo": {
            "total_registros": len(df),
            "total_colunas": len(df.columns),
            "metricas_identificadas": len(metrics),
            "analise_temporal_disponivel": trends["disponivel"],
        },
        "perfil_dados": profile,
        "metricas_identificadas": metrics,
        "estatisticas": descriptive,
        "tendencias": trends,
        "anomalias": anomalies,
    }
