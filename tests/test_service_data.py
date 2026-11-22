"""
=======================================================================
            TESTE SERVICE  ANALYTICS -> ANALISE DADOS ARQUIVO
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
from src.services import service_analytics_ as analytics_service

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # 2. APLICAÇÃO DE TESTES
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.1 TESTE UNITÁRIO - DATAFRAME VÁLIDO
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_analytics_rejeita_entrada_que_nao_e_dataframe():
    with pytest.raises(TypeError, match="A entrada deve ser um DataFrame"):
        analytics_service.service_analytics([1, 2, 3])

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.1 TESTE UNITÁRIO - DATAFRAME VAZIO
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_analytics_rejeita_dataframe_vazio():
    df = pd.DataFrame(columns=["vendas"])

    with pytest.raises(ValueError, match="Não existem registros para analisar"):
        analytics_service.service_analytics(df)

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.1 TESTE UNITÁRIO - ANALISE DE DADOS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_analytics(monkeypatch):
    df = pd.DataFrame({
        "vendas": [100, 200, 300],
        "clientes": [10, 20, 30],
    })

    monkeypatch.setattr(
        analytics_service,
        "estrutura_dados",
        lambda df: {"perfil": "dados"},
    )

    monkeypatch.setattr(
        analytics_service,
        "identificacao_metricas",
        lambda df: {"metricas": "identificadas"},
    )

    monkeypatch.setattr(
        analytics_service,
        "calculo_metricas",
        lambda df: {"estatisticas": "descritivas"},
    )

    monkeypatch.setattr(
        analytics_service,
        "calculo_anaise_temporais",
        lambda df, date_column=None: {
            "disponivel": True,
            "tendencias": "temporais",
        },
    )

    monkeypatch.setattr(
        analytics_service,
        "calculo_anomalias",
        lambda df: {"anomalias": "detectadas"},
    )

    resultado = analytics_service.service_analytics(df)

    assert resultado["resumo"]["total_registros"] == 3
    assert resultado["resumo"]["total_colunas"] == 2

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.1 TESTE UNITÁRIO - ANALISE TEMPORAL
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_analytics_rejeita_resultado_temporal_sem_disponibilidade(monkeypatch):
    """O resumo deve refletir a disponibilidade da análise temporal."""

    df = pd.DataFrame({"vendas": [100, 200]})

    monkeypatch.setattr(analytics_service, "estrutura_dados", lambda df: {})
    monkeypatch.setattr(analytics_service, "identificacao_metricas", lambda df: [])
    monkeypatch.setattr(analytics_service, "calculo_metricas", lambda df: {})
    monkeypatch.setattr(
        analytics_service,
        "calculo_anaise_temporais",
        lambda df, date_column=None: {"disponivel": False},
    )
    monkeypatch.setattr(analytics_service, "calculo_anomalias", lambda df: [])

    resultado = analytics_service.service_analytics(df)

    assert resultado["resumo"]["analise_temporal_disponivel"] is False


def test_analytics_retorna_os_valores_reais_dos_kpis():
    df = pd.DataFrame({
        "data": ["2025-01-01", "2025-01-02"],
        "vendas": [100, 125],
        "clientes": [10, 12],
    })

    resultado = analytics_service.service_analytics(df)

    assert resultado["valores_kpis"]["vendas"] == [100, 125]
    assert resultado["valores_kpis"]["clientes"] == [10, 12]

    vendas = next(
        metrica
        for metrica in resultado["metricas_identificadas"]
        if metrica["nome"] == "vendas"
    )
    assert vendas["valores"] == [100, 125]


