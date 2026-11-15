"""
=======================================================================
            TESTE SERVICE API GEMINI -> IA
=======================================================================


Descrição:
Teste criado para validar o funcionamento do service de comunicação com a API Gemini do sistema.


Responsabilidades:
Responsável por testar a comunicação com a API Gemini, garantindo que o service funcione corretamente e que as respostas da API estejam de acordo com o esperado.
"""


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                    # 1. IMPORTAÇÕES DAS BIBLIOTECAS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
import pytest
from unittest.mock import Mock
from src.services.api import service_gemini


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # 2. APLICAÇÃO DE TESTES
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.1 TESTE UNITÁRIO - CLIENT API GEMINI
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_client_api_gemini(monkeypatch):
    """
    Teste unitário responsável por validar a criação do cliente da API Gemini.
    """
    mock_client = Mock()
    criar_cliente = Mock(return_value=mock_client)
    monkeypatch.setattr(service_gemini, "GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setattr(service_gemini, "GEMINI_TIMEOUT_SECONDS", 30)
    monkeypatch.setattr(service_gemini, "GEMINI_MAX_OUTPUT_TOKENS", 1000)
    monkeypatch.setattr(service_gemini.genai, "Client", criar_cliente)

    client = service_gemini.client_api_gemini()

    assert client is mock_client
    criar_cliente.assert_called_once()


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.2 TESTE UNITÁRIO - CHAVE API AUSENTE
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_client_api_gemini_sem_chave(monkeypatch):
    """
    O serviço deve rejeitar a criação do cliente sem chave de API.
    """
    criar_cliente = Mock()
    monkeypatch.setattr(service_gemini, "GEMINI_API_KEY", None)
    monkeypatch.setattr(service_gemini.genai, "Client", criar_cliente)

    with pytest.raises(
        service_gemini.GeminiServiceError,
        match="GEMINI_API_KEY não foi configurada",
    ):
        service_gemini.client_api_gemini()

    criar_cliente.assert_not_called()


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.3 TESTE UNITÁRIO - FALHA AO CRIAR CLIENTE
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_client_api_gemini_erro_ao_criar_cliente(monkeypatch):
    monkeypatch.setattr(service_gemini, "GEMINI_API_KEY", "chave-de-teste")
    monkeypatch.setattr(
        service_gemini.genai,
        "Client",
        Mock(side_effect=RuntimeError("falha interna")),
    )

    with pytest.raises(
        service_gemini.GeminiServiceError,
        match="Não foi possível criar o cliente da Gemini API",
    ) as exc_info:
        service_gemini.client_api_gemini()

    assert isinstance(exc_info.value.__cause__, RuntimeError)

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.4 TESTE UNITÁRIO - RETORNA TEXTO
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def test_analise_indicadores_gemini_retorna_texto(monkeypatch):
    resposta_api = Mock(text="  Análise concluída.  ")
    cliente = Mock()
    cliente.models.generate_content.return_value = resposta_api

    monkeypatch.setattr(
        service_gemini,
        "client_api_gemini",
        Mock(return_value=cliente),
    )

    resultado = service_gemini.analise_indicadores_gemini("Analise os indicadores de vendas.")

    assert resultado == "Análise concluída."
    cliente.models.generate_content.assert_called_once()

    argumentos = cliente.models.generate_content.call_args.kwargs
    assert argumentos["model"] == service_gemini.GEMINI_MODEL
    assert argumentos["contents"] == "Analise os indicadores de vendas."
    cliente.close.assert_called_once()


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.5 TESTE UNITÁRIO - PROMPT VAZIO
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
@pytest.mark.parametrize("prompt", ["", "   ", None])
def test_analise_indicadores_gemini_rejeita_prompt_vazio(prompt, monkeypatch):
    criar_cliente = Mock()
    monkeypatch.setattr(service_gemini, "client_api_gemini", criar_cliente)

    with pytest.raises(ValueError, match="prompt de análise não pode estar vazio"):
        service_gemini.analise_indicadores_gemini(prompt)

    criar_cliente.assert_not_called()


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 2.6 TESTE UNITÁRIO - RESPOSTA VAZIA
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
@pytest.mark.parametrize("texto_resposta", [None, "", "   "])
def test_analise_indicadores_gemini_rejeita_resposta_vazia(
    texto_resposta,
    monkeypatch,
):
    cliente = Mock()
    cliente.models.generate_content.return_value = Mock(text=texto_resposta)
    monkeypatch.setattr(
        service_gemini,
        "client_api_gemini",
        Mock(return_value=cliente),
    )

    with pytest.raises(
        service_gemini.GeminiServiceError,
        match="Gemini API retornou uma resposta vazia",
    ):
        service_gemini.analise_indicadores_gemini("Gere uma análise.")

    cliente.close.assert_called_once()
