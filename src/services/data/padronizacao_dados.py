"""
=======================================================================
            SERVICE DATA -> PADRONIZAÇÃO DATAFRAME
=======================================================================


Descrição:
Service que possui objetivo de aplicar padronizações nas bases de dados. Aplicando tratativas nas colunas e identificando inconsistencias como valores nulos e duplicados.


Responsabilidades:
Aplicar padronizações nas bases de dados e identificar inconsistencias de valores nulos e duplicados nas bases de dados

"""


import re
import pandas as pd

def padronizacao(name: object) -> str:

    """
    Função para padronizar o nome das colunas das bases de dados
    """
    value = str(name).strip().lower()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^\w]", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def limpeza_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Função para aplicar limpeza no dataframe da base de dados. Desta forma, aplicando normalização nas colunas, dados e 
    identificando valores inconsistentes
    
    """

    result = df.copy()
    warnings = []

    original_columns = list(result.columns)
    standardized_columns = [padronizacao(column)
        for column in original_columns
    ]

    if standardized_columns != original_columns:
        result.columns = standardized_columns
        warnings.append("Os nomes das colunas foram padronizados.")

    text_columns = result.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        result[column] = result[column].map(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    if text_columns.size:
        warnings.append("Espaços externos foram removidos de valores textuais.")

    missing_count = int(result.isna().sum().sum())

    if missing_count:
        warnings.append(f"Foram encontrados {missing_count} valores ausentes. Eles foram preservados para tratamento posterior.")

    duplicate_count = int(result.duplicated().sum())

    if duplicate_count:
        warnings.append(f"Foram identificadas {duplicate_count} linhas duplicadas; elas foram preservadas.")

    return result, warnings
