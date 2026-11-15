"""
=======================================================================
            SERVICE INPUT DADOS -> INGESTÃO DE ARQUIVO
=======================================================================


Descrição:
Service responsável por orquestrar a ingestão, validação e padronização dos dados recebidos em um arquivo.


Responsabilidades:
Validar o formato do arquivo e o dataframe, padronizar os dados e gerar um relatório de qualidade.

"""

from typing import BinaryIO
import pandas as pd

from .data.validacao_formato_arquivo import validacao_formato_arquivo
from .data.validacao_dataframe import validacao_dataframe
from .data.padronizacao_dados import limpeza_dataframe
from .data.report_qualidade_dados import report_qualidade_dados


def service_ingestao_arquivo( file: BinaryIO, filename: str,) -> dict:
    """
    Função responsável por orquestrar e executar a ingestão completa dos dados de entrada do sistema.

    Entradas:

        * Arquivo de entrada (BinaryIO)
        * Nome do arquivo

    Saídas:
        Retorna um dicionário contendo:
        * dataframe: dados preparados para análise.
        * nome_arquivo: nome do arquivo de entrada.
        * relatorio_qualidade: resumo da qualidade dos dados.
        * avisos: alterações e problemas não impeditivos.

    Exceções:
        ValueError: quando os dados não passam pela validação inicial ou após a padronização.
    
    """

    dataframe = validacao_formato_arquivo(file, filename)

    errors = validacao_dataframe(dataframe)

    if errors:
        raise ValueError("A base não passou pela validação: " + " ".join(errors))
 
    dataframe, warnings = limpeza_dataframe(dataframe)

    errors_after_cleaning = validacao_dataframe(dataframe)

    if errors_after_cleaning:
        raise ValueError(
            "A base ficou inválida após a padronização: " + " ".join(errors_after_cleaning))

    report = report_qualidade_dados(dataframe, filename)

    return {
        "dataframe": dataframe,
        "nome_arquivo": filename,
        "relatorio_qualidade": report,
        "avisos": warnings,
    } 

    
