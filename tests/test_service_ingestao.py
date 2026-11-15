"""
=======================================================================
            TESTE SERVICE INPUT DADOS -> INGESTÃO DE ARQUIVO
=======================================================================


Descrição:
Teste criado para validar o funcionamento do service de ingestão de dados de entrada do sistema.


Responsabilidades:
Responsável por testar a ingestão, validação e padronização dos dados recebidos em um arquivo, garantindo que o service funcione corretamente e que os dados estejam prontos para análise.
"""

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                    # 1. IMPORTAÇÕES DAS BIBLIOTECAS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
import pandas as pd
import pytest
from src.services import service_ingestao_dados_input


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # 2. APLICAÇÃO DE TESTES
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.1 TESTE UNITÁRIO - ENTRADA ARQUIVO VÁLIDO
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_service_ingestao_arquivo(monkeypatch):
    """
    Teste unitário responsável por validar, limpar e retornar os dados corretos do dataframe.
    """

    df_original = pd.DataFrame({
        "vendas": [100, 200, 300],
        "clientes": [10, 20, 30],
    })

    df_limpo = df_original.copy()
    avisos_esperados = ["Dados padronizados"]
    relatorio_esperado = {"total_registros": 3}

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "validacao_formato_arquivo",
        lambda file, filename: df_original,
    )

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "validacao_dataframe",
        lambda df: [],
    )

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "limpeza_dataframe",
        lambda df: (df_limpo, avisos_esperados),
    )

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "report_qualidade_dados",
        lambda df, filename: relatorio_esperado,
    )

    resultado = service_ingestao_dados_input.service_ingestao_arquivo(
        file=None,
        filename="arquivo_teste.csv",
    )

    assert resultado["dataframe"] is df_limpo
    assert resultado["nome_arquivo"] == "arquivo_teste.csv"
    assert resultado["relatorio_qualidade"] == relatorio_esperado
    assert resultado["avisos"] == avisos_esperados

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # 2.2 TESTE UNITÁRIO - ENTRADA ARQUIVO DADOS INVALIDOS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_service_ingestao_arquivo_dados_invalidos(monkeypatch):


    df = pd.DataFrame({"vendas": [100]})

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "validacao_formato_arquivo",
        lambda file, filename: df,
    )

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "validacao_dataframe",
        lambda dataframe: ["A base não possui dados válidos"],
    )

    with pytest.raises(ValueError, match="A base não passou pela validação"):
        service_ingestao_dados_input.service_ingestao_arquivo(
            file=None,
            filename="invalido.csv",
        )

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # 2.3 TESTE UNITÁRIO - ENTRADA ARQUIVO DADOS INVALIDOS APÓS LIMPEZA
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_ingestao_rejeita_dados_invalidos_apos_limpeza(monkeypatch):
    """Deve validar os dados novamente depois da padronização."""

    df = pd.DataFrame({"vendas": [100]})
    validacoes = iter([[], ["Dados inválidos após limpeza"]])

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "validacao_formato_arquivo",
        lambda file, filename: df,
    )

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "validacao_dataframe",
        lambda dataframe: next(validacoes),
    )

    monkeypatch.setattr(
        service_ingestao_dados_input,
        "limpeza_dataframe",
        lambda dataframe: (dataframe, []),
    )

    with pytest.raises(ValueError, match="A base ficou inválida após a padronização",):
        service_ingestao_dados_input.service_ingestao_arquivo(
            file=None,
            filename="vendas.csv",
        )


    