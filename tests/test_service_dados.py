import pandas as pd
import pytest

from services.service_dados import ServiceDados


def test_leitura_arquivo_csv(tmp_path):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text(
        "mes,receita\nJan,100\nFev,120\n",
        encoding="utf-8",
    )

    resultado = ServiceDados.leitura_arquivo(arquivo)

    assert list(resultado.columns) == ["mes", "receita"]
    assert resultado["receita"].tolist() == [100, 120]


def test_leitura_arquivo_excel(tmp_path):
    arquivo = tmp_path / "dados.xlsx"
    dados = pd.DataFrame({
        "mes": ["Jan", "Fev"],
        "receita": [100, 120],
    })
    dados.to_excel(arquivo, index=False)

    resultado = ServiceDados.leitura_arquivo(arquivo)

    pd.testing.assert_frame_equal(resultado, dados)


def test_validacao_extensao_rejeita_arquivo_invalido(tmp_path):
    arquivo = tmp_path / "dados.txt"

    with pytest.raises(ValueError, match="Extensão de arquivo inválida"):
        ServiceDados.validacao_extensao(arquivo)


def test_validacao_extensao_rejeita_arquivo_none():
    with pytest.raises(ValueError, match="Nenhum arquivo foi enviado"):
        ServiceDados.validacao_extensao(None)


@pytest.mark.parametrize(
    "df",
    [
        None,
        pd.DataFrame(),
    ],
)
def test_validar_dataframe_rejeita_dados_invalidos(df):
    with pytest.raises(ValueError):
        ServiceDados.validar_dataframe(df)