"""
=======================================================================
            ANALYZER -> ESTATÍSTICAS DESCRITIVAS
=======================================================================


Descrição:
Módulo responsável pelo cálculo de estatísticas descritivas das colunas numéricas.


Responsabilidades:
Calcular quantidade de valores válidos, média, mediana, mínimo, máximo, desvio padrão e soma.

"""


import pandas as pd

def calculo_metricas(df: pd.DataFrame) -> dict:
    """
    Função com o objetivo de calcular estatísticas descritivas das colunas numéricas.

    Entradas:
        * Dataframe a ser analisado

    Saídas:
        Retorna um dicionário indexado pelo nome de cada coluna numérica,
        contendo suas estatísticas descritivas.
    """

    results = {}

    df_tipos_dados_numericos = df.select_dtypes(include="number")

    for column in df_tipos_dados_numericos.columns:
        if pd.api.types.is_bool_dtype(df_tipos_dados_numericos[column]):
            continue

        series = df_tipos_dados_numericos[column].dropna()

        if series.empty:
            continue

        results[str(column)] = {
            "quantidade": int(series.count()),
            "media": float(series.mean()),
            "mediana": float(series.median()),
            "minimo": float(series.min()),
            "maximo": float(series.max()),
            "desvio_padrao": (
                float(series.std())
                if len(series) > 1
                else None
            ),
            "soma": float(series.sum()),
        }

    return results