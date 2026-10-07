from unittest.mock import Mock, patch

import pytest

from frontend.components.analytics import _gerar_diagnostico
from prompts.prompt import criar_prompt_diagnostico
from services.service_api_gemini import ServiceApiGemini


def test_gemini_service_rejeita_chave_ausente():
    with patch("services.service_api_gemini.load_dotenv"), patch.dict(
        "os.environ", {}, clear=True
    ):
        with pytest.raises(ValueError, match="CHAVE_API"):
            ServiceApiGemini()


def test_envio_diagnostico_envia_prompt_e_retorna_resposta():
    client = Mock()
    client.models.generate_content.return_value.text = "  Diagnóstico de teste.  "

    with patch("services.service_api_gemini.load_dotenv"), patch(
        "services.service_api_gemini.genai.Client", return_value=client
    ):
        service = ServiceApiGemini(api_key="test-key", model="test-model")
        resultado = service.envio_diagnostico("Analise os KPIs.")

    assert resultado == "Diagnóstico de teste."
    client.models.generate_content.assert_called_once_with(
        model="test-model",
        contents="Analise os KPIs.",
    )


def test_envio_diagnostico_rejeita_prompt_vazio():
    with patch("services.service_api_gemini.load_dotenv"), patch(
        "services.service_api_gemini.genai.Client"
    ):
        service = ServiceApiGemini(api_key="test-key")

    with pytest.raises(ValueError, match="prompt"):
        service.envio_diagnostico("  ")


def test_gerar_diagnostico_usa_servico_gemini():
    with patch(
        "frontend.components.analytics.criar_prompt_diagnostico",
        return_value="prompt de teste",
    ), patch(
        "frontend.components.analytics.ServiceApiGemini"
    ) as servico_gemini:
        servico_gemini.return_value.envio_diagnostico.return_value = "Diagnóstico"

        resultado = _gerar_diagnostico({"total_kpis": 1})

    assert resultado == "Diagnóstico"
    servico_gemini.assert_called_once_with()
    servico_gemini.return_value.envio_diagnostico.assert_called_once_with(
        "prompt de teste"
    )


def test_criar_prompt_inclui_indicadores_e_dados():
    prompt = criar_prompt_diagnostico(
        {
            "total_kpis": 1,
            "kpis": {
                "Faturamento": {
                    "variation": -21.0,
                    "status": "Queda significativa",
                }
            },
        }
    )

    assert "Faturamento" in prompt
    assert "-21.0" in prompt
    assert "Queda significativa" in prompt
