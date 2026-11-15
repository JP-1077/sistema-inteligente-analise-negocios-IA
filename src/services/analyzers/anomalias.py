"""
=======================================================================
            ANALYZER -> DETECÇÃO DE ANOMALIAS
=======================================================================


Descrição:
Módulo responsável por identificar possíveis valores atípicos em colunas numéricas pelo método IQR.


Responsabilidades:
Calcular os limites inferior e superior do método IQR e listar valores que estejam fora desses limites.

"""


import pandas as pd


def calculo_anomalias(df: pd.DataFrame) -> dict:
    """
    Função com o objetivo de sinalizar possíveis valores atípicos pelo método IQR.

    Entradas:
        * Dataframe a ser analisado

    Saídas:
        Retorna um dicionário indexado pelo nome da coluna, com o método utilizado,
        os limites calculados, a quantidade de anomalias, seus índices e valores.
    """

    results = {}

    for column in df.select_dtypes(include="number").columns:
        if pd.api.types.is_bool_dtype(df[column]):
            continue

        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        mask = (series < lower_bound) | (series > upper_bound)

        results[str(column)] = {
            "metodo": "IQR",
            "limite_inferior": float(lower_bound),
            "limite_superior": float(upper_bound),
            "quantidade_anomalias": int(mask.sum()),
            "indices": [
                int(index) if isinstance(index, int) else str(index)
                for index in series.index[mask]
            ],
            "valores": [
                float(value) for value in series[mask].tolist()
            ],
        }

    return results