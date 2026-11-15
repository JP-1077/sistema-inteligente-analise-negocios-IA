import pandas as pd


def estrutura_dados(df: pd.DataFrame) -> dict:

    colunas_numericas = [
        col for col in df.select_dtypes(include="number").columns
        if not pd.api.types.is_bool_dtype(df[col])
    ]

    colunas_data = list(
        df.select_dtypes(include=["datetime", "datetimetz"]).columns
    )

    colunas_categoricas = list(
        df.select_dtypes(include=["object", "category", "string"]).columns
    )

    return {
        "total_registros": int(len(df)),
        "total_colunas": int(len(df.columns)),
        "colunas_numericas": [str(col) for col in colunas_numericas],
        "colunas_data": [str(col) for col in colunas_data],
        "colunas_categoricas": [str(col) for col in colunas_categoricas],
        "valores_ausentes": {
            str(col): int(total)
            for col, total in df.isna().sum().items()
        },
    }
