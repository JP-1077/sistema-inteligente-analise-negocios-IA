"""
=======================================================================
            SERVICE DATA -> LEITURA E VALIDACAO FORMATO ARQUIVO
=======================================================================


Descrição:
Service que possui objetivo de realizar uma leitura inicial do arquivo de entrada, aplicar validações no formato do arquivo e 
retornar um dataframe para ser utilizados nos demais serviços do sistema.


Responsabilidades:
Validar arquivo de entrada e seu formato e retorna dataframe.

"""

from pathlib import Path
import pandas as pd
from typing import BinaryIO
from io import BytesIO
import logging
import warnings

extensoes_aceitas = [".csv", ".xlsx", ".xls"]


def validacao_formato_arquivo(arquivo: BinaryIO, nomearquivo: str) -> pd.DataFrame:
    """
    Função com o objetivo de realizar a leitura inicial do arquivo, validar formato do arquivo e retornar um data frame do arquivo

    Entradas:
        * Nome Arquivo
        * Arquivo
    
    Saídas:
        Retorna um dataframe com base no arquivo de entrada.
    """

    extensao = Path(nomearquivo).suffix.lower()

    if extensao not in extensoes_aceitas:
        raise ValueError(f"Formato de arquivo enviado não suportado pelo sistema. Desta forma, envie como entrada um arquivo CSV ou XLSX.")

    try:
        if extensao == ".csv":
            if hasattr(arquivo, "seek"):
                arquivo.seek(0)

            try:
                df = pd.read_csv(arquivo, encoding="utf-8-sig")
            except UnicodeDecodeError:
                if hasattr(arquivo, "seek"):
                    arquivo.seek(0)
                df = pd.read_csv(arquivo, encoding="latin-1")

        else:
            if hasattr(arquivo, "seek"):
                arquivo.seek(0)

            df = pd.read_excel(arquivo, engine="openpyxl")

    except (pd.errors.ParserError, ValueError, OSError) as exc:
        raise ValueError(f"Não foi possível interpretar o arquivo '{nomearquivo}'.") from exc

    if df.empty:
        raise ValueError("O arquivo não possui registros.")

    return df