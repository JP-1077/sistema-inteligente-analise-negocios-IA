"""
=======================================================================
            SERVICE DATA -> RELATÓRIO DE QUALIDADE DOS DADOS
=======================================================================


Descrição:
Service responsável por gerar um relatório com metadados do arquivo, uma amostra do dataframe e indicadores de qualidade dos dados.


Responsabilidades:
Consolidar informações do arquivo e identificar valores ausentes e linhas duplicadas no dataframe.

"""


import pandas as pd
from pathlib import Path
from typing import Any

def report_qualidade_dados(df: pd.DataFrame, nome_arquivo: str, tamanho_arquivo: int | None = None, limite_linhas_amostra: int = 5,) -> dict[str, Any]:
    """
    Função com o objetivo de gerar um relatório de qualidade dos dados e metadados do arquivo.

    Entradas:
        * Dataframe
        * Nome do arquivo
        * Tamanho do arquivo em bytes (opcional)
        * Limite de linhas da amostra (opcional)

    Saídas:
        Retorna um dicionário com os metadados do arquivo, uma amostra do dataframe e indicadores de qualidade dos dados.

    Validações:
        * O dataframe deve ser uma instância de pandas.DataFrame.
        * O limite de linhas da amostra não pode ser negativo.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("O parâmetro 'df' deve ser um DataFrame.")

    if limite_linhas_amostra < 0:
        raise ValueError("O limite da amostra não pode ser negativo.")

    total_linhas_arquivo = len(df)
    total_colunas_arquivo = len(df.columns)

    valores_ausentes = df.isna().sum()
    total_valores_ausentes = int(valores_ausentes.sum())

    extensao = Path(nome_arquivo).suffix.lower().lstrip(".")

    colunas = [
        {
            "nome": str(coluna),
            "tipo": str(df[coluna].dtype),
            "valores_ausentes": int(valores_ausentes[coluna]),
            "percentual_ausente": round(
                float(valores_ausentes[coluna] / total_linhas_arquivo * 100),
                2,
            ) if total_linhas_arquivo else 0.0,
            "valores_unicos": int(df[coluna].nunique(dropna=True)),
        }
        for coluna in df.columns
    ]

    return {
        "metadados_arquivo": {
            "nome_arquivo": Path(nome_arquivo).name,
            "extensao": extensao.upper() or "Desconhecida",
            "tamanho_bytes": tamanho_arquivo,
            "tamanho_kb": (
                round(tamanho_arquivo / 1024, 2)
                if tamanho_arquivo is not None
                else None
            ),
            "total_registros": total_linhas_arquivo,
            "total_colunas": total_colunas_arquivo,
            "nomes_colunas": [str(coluna) for coluna in df.columns],
        },
        "amostra_dataframe": df.head(limite_linhas_amostra).copy(),
        "qualidade_dados": {
            "colunas": colunas,
            "linhas_duplicadas": int(df.duplicated().sum()),
            "total_valores_ausentes": total_valores_ausentes,
            "percentual_valores_ausentes": round(
                total_valores_ausentes / (total_linhas_arquivo * total_colunas_arquivo) * 100,
                2,
            ) if total_linhas_arquivo and total_colunas_arquivo else 0.0,
        },
    }
   