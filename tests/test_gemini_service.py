from unittest.mock import Mock, patch

import pytest

from prompts.business_diagnostic_prompt import criar_prompt_diagnostico
from services.gemini_service import GeminiService


def test_gemini_service_rejeita_chave_ausente():
    with patch("services.gemini_service.load_dotenv"), patch.dict(
        "os.environ", {}, clear=True
    ):
        with pytest.raises(ValueError, match="CHAVE_API"):
            GeminiService()


def test_gerar_diagnostico_envia_prompt_e_retorna_resposta():
    client = Mock()
    client.models.generate_content.return_value.text = "  Diagnóstico de teste.  "

    with patch("services.gemini_service.load_dotenv"), patch(
        "services.gemini_service.genai.Client", return_value=client
    ):
        service = GeminiService(api_key="test-key", model="test-model")
        resultado = service.gerar_diagnostico("Analise os KPIs.")

    assert resultado == "Diagnóstico de teste."
    client.models.generate_content.assert_called_once_with(
        model="test-model",
        contents="Analise os KPIs.",
    )


def test_gerar_diagnostico_rejeita_prompt_vazio():
    with patch("services.gemini_service.load_dotenv"), patch(
        "services.gemini_service.genai.Client"
    ):
        service = GeminiService(api_key="test-key")

    with pytest.raises(ValueError, match="prompt"):
        service.gerar_diagnostico("  ")


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
