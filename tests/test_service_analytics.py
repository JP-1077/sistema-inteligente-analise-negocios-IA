import pandas as pd
import pytest

from services.service_analytics import KPIanaliser


def test_identifica_kpis_retorna_apenas_colunas_numericas():
    df = pd.DataFrame({
        "mes": ["Jan", "Fev"],
        "receita": [100, 80],
        "clientes": [10, 12],
    })

    assert KPIanaliser.identifica_kpis(df) == ["receita", "clientes"]


def test_compara_periodos_detecta_queda():
    df = pd.DataFrame({"receita": [100, 80]})

    resultado = KPIanaliser.compara_periodos(df, "receita")

    assert resultado["previous_value"] == 100
    assert resultado["current_value"] == 80
    assert resultado["variation"] == -20.0
    assert resultado["status"] == "Queda significativa"
    assert KPIanaliser.detecta_declinio(df, "receita")


@pytest.mark.parametrize(
    ("valor_anterior", "valor_atual"),
    [(0, 100), (None, 100), (100, None)],
)
def test_calcula_variacao_retorna_none_sem_base_valida(valor_anterior, valor_atual):
    assert KPIanaliser.calcula_variacao(valor_anterior, valor_atual) is None


def test_calcula_estatisticas_e_detecta_anomalia():
    df = pd.DataFrame({"vendas": [10] * 10 + [100]})

    assert KPIanaliser.calcula_media(df, "vendas") == 18.18
    assert KPIanaliser.calculate_max(df, "vendas") == 100
    assert KPIanaliser.calculate_min(df, "vendas") == 10
    assert KPIanaliser.detecta_anomalia(df, "vendas") == [100]


def test_analise_retorna_resumo_dos_kpis():
    df = pd.DataFrame({
        "receita": [100, 95, 80],
        "clientes": [10, 12, 15],
        "mes": ["Jan", "Fev", "Mar"],
    })

    resultado = KPIanaliser.analise(df)

    assert resultado["total_registros"] == 3
    assert resultado["total_kpis"] == 2
    assert resultado["kpis"]["receita"]["variation"] == -20.0
    assert resultado["kpis"]["receita"]["trend"] == "queda"
    assert resultado["kpis"]["clientes"]["trend"] == "crescimento"


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame(),
        pd.DataFrame({"categoria": ["A", "B"]}),
    ],
)
def test_analise_rejeita_dataframe_sem_kpis(df):
    with pytest.raises(ValueError):
        KPIanaliser.analise(df)