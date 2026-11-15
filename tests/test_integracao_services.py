from io import BytesIO
from unittest.mock import Mock

from src.services import service_analytics_ as analytics_service
from src.services import service_ingestao_dados_input as ingestao_service
from src.services.api import service_gemini
from src.prompts.prompt import criar_prompt_diagnostico


def test_fluxo_completo_ingestao_analise_e_diagnostico(monkeypatch):
    conteudo_csv = (
        "Data,Vendas,Clientes\n"
        "2025-01-01,100,10\n"
        "2025-01-02,110,11\n"
        "2025-01-03,120,12\n"
        "2025-01-04,1000,100\n"
    )
    arquivo = BytesIO(conteudo_csv.encode("utf-8"))

    ingestao = ingestao_service.service_ingestao_arquivo(
        file=arquivo,
        filename="vendas.csv",
    )

    assert ingestao["nome_arquivo"] == "vendas.csv"
    assert list(ingestao["dataframe"].columns) == ["data", "vendas", "clientes"]
    assert ingestao["relatorio_qualidade"]["metadados_arquivo"][
        "total_registros"
    ] == 4

    analise = analytics_service.service_analytics(
        ingestao["dataframe"],
        date_column="data",
    )

    assert analise["resumo"]["total_registros"] == 4
    assert analise["resumo"]["total_colunas"] == 3
    assert analise["resumo"]["analise_temporal_disponivel"] is True
    assert analise["estatisticas"]["vendas"]["soma"] == 1330.0
    assert analise["anomalias"]["vendas"]["quantidade_anomalias"] == 1

    prompt = criar_prompt_diagnostico(analise)
    resposta = "As vendas cresceram no período, mas o último valor é uma anomalia."
    cliente = Mock()
    cliente.models.generate_content.return_value = Mock(text=f"  {resposta}  ")
    monkeypatch.setattr(
        service_gemini,
        "client_api_gemini",
        Mock(return_value=cliente),
    )

    diagnostico = service_gemini.analise_indicadores_gemini(prompt)

    assert diagnostico == resposta
    cliente.models.generate_content.assert_called_once()
    chamada = cliente.models.generate_content.call_args.kwargs
    assert chamada["contents"] == prompt
    assert "1330.0" in prompt
    cliente.close.assert_called_once()