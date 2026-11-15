"""
=======================================================================
            ANALYZER -> MÉTRICAS TEMPORAIS
=======================================================================


Descrição:
Módulo responsável por comparar os valores médios das métricas numéricas entre os dois períodos mais recentes.


Responsabilidades:
Identificar ou receber uma coluna temporal e calcular variações absolutas e percentuais por métrica.

"""


import pandas as pd

def calculo_anaise_temporais( df: pd.DataFrame, date_column: str | None = None) -> dict:
    """
    Função com o objetivo de calcular tendências temporais para as métricas numéricas.

    Entradas:
        * Dataframe a ser analisado
        * Nome da coluna temporal (opcional; quando omitido, tenta identificar uma coluna temporal)

    Saídas:
        Retorna um dicionário com a disponibilidade da análise, a coluna temporal,
        os resultados por métrica e, quando aplicável, o motivo da indisponibilidade.

    Exceções:
        ValueError: quando a coluna temporal informada não existe no dataframe.
    """

    if date_column is None:
        datetime_columns = list(
            df.select_dtypes(include=["datetime", "datetimetz"]).columns)

        if not datetime_columns:
            return {
                "disponivel": False,
                "motivo": "Nenhuma coluna temporal identificada.",
                "resultados": {},
            }

        date_column = str(datetime_columns[0])

    if date_column not in df.columns:
        raise ValueError(f"A coluna temporal '{date_column}' não existe.")

    dates = pd.to_datetime(df[date_column], errors="coerce")

    numeric_columns = [
        col for col in df.select_dtypes(include="number").columns
        if not pd.api.types.is_bool_dtype(df[col])
    ]

    results = {}

    for column in numeric_columns:
        data = pd.DataFrame({
            "data": dates,
            "valor": df[column],
        }).dropna()

        if data.empty:
            continue

        daily = (data.groupby(data["data"].dt.floor("D"))["valor"].mean().sort_index())

        if len(daily) < 2:
            continue

        previous = float(daily.iloc[-2])
        current = float(daily.iloc[-1])
        variation = current - previous

        percentage = (
            (variation / abs(previous)) * 100
            if previous != 0
            else None
        )

        results[str(column)] = {
            "data_anterior": daily.index[-2].isoformat(),
            "data_atual": daily.index[-1].isoformat(),
            "valor_anterior": previous,
            "valor_atual": current,
            "variacao_absoluta": variation,
            "variacao_percentual": percentage,
            "direcao": (
                "aumento" if variation > 0
                else "queda" if variation < 0
                else "estavel"
            ),
        }

    return {
        "disponivel": bool(results),
        "coluna_temporal": date_column,
        "resultados": results,
        "motivo": (
            None if results else
            "Não existem períodos comparáveis com valores válidos."
        ),
    }
