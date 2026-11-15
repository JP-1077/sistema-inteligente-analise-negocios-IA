"""
=======================================================================
            SERVICE DATA -> VALIDAÇÃO DATAFRAME
=======================================================================


Descrição:
Service que possui objetivo de realizar determinadas validações na base de dados de entrada.


Responsabilidades:
Aplicar validações nos dados da base de dados e encontrar inconsistencias nas bases.

"""

import pandas as pd


def validacao_dataframe(df: pd.DataFrame) -> list[str]:
    """
    Função com o objetivo de realizar determinadas validações na base de dados de entrada 

    Entradas:
        * Dataframe
    
    Saídas:
        Retorna uma lista de erros que foram encontrados após a aplicação do service.
    """

    errors = []

    if df.empty:
        errors.append("A base não possui registros.")

    if len(df.columns) == 0:
        errors.append("A base não possui colunas.")

    if all(
        str(column).strip() == ""
        or str(column).lower().startswith("unnamed:")
        for column in df.columns
    ):
        errors.append("Não foram encontrados nomes de colunas válidos.")

    normalized_names = [
        str(column).strip().casefold()
        for column in df.columns
    ]

    if len(normalized_names) != len(set(normalized_names)):
        errors.append("Existem nomes de colunas duplicados ou equivalentes após a padronização.")

    if len(df.columns) > 500:
        errors.append("A base excede o limite inicial de 500 colunas.")

    return errors
