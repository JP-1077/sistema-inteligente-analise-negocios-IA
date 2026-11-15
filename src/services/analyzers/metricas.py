"""
=======================================================================
            ANALYZER -> IDENTIFICAÇÃO DE MÉTRICAS
=======================================================================


Descrição:
Módulo responsável por identificar métricas numéricas disponíveis para análise.


Responsabilidades:
Percorrer as colunas numéricas e descrever as análises disponíveis para cada métrica.

"""


import pandas as pd


def identificacao_metricas(df: pd.DataFrame) -> list[dict]:
    """
    Função com o objetivo de identificar as métricas numéricas do dataframe.

    Entradas:
        * Dataframe a ser analisado

    Saídas:
        A função está anotada para retornar uma lista de dicionários com o nome,
        tipo, quantidade de registros válidos, valores únicos e análises disponíveis.
    """

    metricas = []

    for column in df.select_dtypes(include="number").columns:
        if pd.api.types.is_bool_dtype(df[column]):
            continue
        
        series = df[column].dropna()

        if series.empty:
            continue

    
        metricas.append({
            "nome": str(column),
            "tipo": "numerica",
            "registros_validos": int(series.count()),
            "valores_unicos": int(series.nunique()),
            "analises_disponiveis": [
            "estatisticas_descritivas",
            "distribuicao",
            "deteccao_anomalias",
        ]

        })

    return metricas