#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                    # 1. IMPORTAÇÕES DAS BIBLIOTECAS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 1.1 IMPORTAÇÕES - LIBS NATIVAS PYTHON
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
import os
import logging

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 1.2 IMPORTAÇÕES - GEMINI API
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 1.3 IMPORTAÇÕES - VARIÁVEIS DE AMBIENTE
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
load_dotenv()


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                    # 2. CONFIGURAÇÕES DE LOGS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",)

logger = logging.getLogger("sistema_inteligente_analise_negocios_IA")


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                    # 3. CONFIGURAÇÕES DA APLICAÇÃO
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/


class GeminiServiceError(Exception):
    pass

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 3.1 CONFIGURAÇÃO DOS PARÂMETROS GEMINI
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash",)

GEMINI_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "60"))

GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2500"))



#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                    # 5. CONFIGURAÇÃO DO CLIENTE GEMINI
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 5.1 CRIAÇÃO DO CLIENTE
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def client_api_gemini():
    """
    Esta função realiza a validação das configurações e a criação
    do cliente responsável pela comunicação com a Gemini API.

    Saída da função:
        Cliente configurado para realizar requisições à Gemini API.

    Exceções:
        GeminiServiceError: quando as configurações são inválidas
        ou ocorre falha na criação do cliente.
    """

    logger.info("ETAPA [SERVICE API GEMINI]: Iniciando configuração do client da API Gemini")

    try:
        if not GEMINI_API_KEY:
            raise GeminiServiceError("GEMINI_API_KEY não foi configurada no arquivo .env.")

        if GEMINI_TIMEOUT_SECONDS <= 0:
            raise GeminiServiceError("O timeout da Gemini API deve ser maior que zero.")

        if GEMINI_MAX_OUTPUT_TOKENS <= 0:
            raise GeminiServiceError("O limite de tokens de saída deve ser maior que zero.")

        cliente = genai.Client(api_key=GEMINI_API_KEY, http_options=types.HttpOptions(timeout=GEMINI_TIMEOUT_SECONDS * 1000,))

        logger.info(f"ETAPA [GEMINI]: Cliente configurado com sucesso | " "Modelo: %s", GEMINI_MODEL)

        return cliente
    
    except GeminiServiceError:
        logger.exception("ETAPA [GEMINI]: Falha na validação das configurações")
        raise 

    except Exception as e:
        logger.exception(f"ETAPA [GEMINI]: Erro ao criar client da API Gemini: {e}")
        raise GeminiServiceError("Não foi possível criar o cliente da Gemini API.") from e


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                    # 6. ENVIO DOS DADOS PARA A GEMINI API
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                # 6.1 ANÁLISE DOS INDICADORES
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def analise_indicadores_gemini(prompt: str) -> str:
    logger.info("[ETAPA ANÁLISE GEMINI]: Iniciando análise dos indicadores")

    cliente = None

    try:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("[ETAPA ANÁLISE GEMINI]: O prompt de análise não pode estar vazio.")

        cliente = client_api_gemini()

        resposta = cliente.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
            ),
        )

        texto_resposta = resposta.text
        if not isinstance(texto_resposta, str) or not texto_resposta.strip():
            raise GeminiServiceError("[ETAPA ANÁLISE GEMINI]: A Gemini API retornou uma resposta vazia.")

        logger.info("[ETAPA ANÁLISE GEMINI]: Análise concluída com sucesso")
        return texto_resposta.strip()

    except ValueError as exc:
        logger.error("[ETAPA ANÁLISE GEMINI]: Entrada inválida: %s", exc)
        raise

    except GeminiServiceError:
        raise

    except errors.APIError as exc:
        codigo_status = getattr(exc, "code", None)

        if codigo_status == 400:
            mensagem = "A solicitação enviada à Gemini API é inválida."
        elif codigo_status in (401, 403):
            mensagem = "Falha de autenticação ou permissão na Gemini API."
        elif codigo_status == 429:
            mensagem = "Limite de requisições ou cota da Gemini API atingido."
        elif codigo_status is not None and codigo_status >= 500:
            mensagem = "A Gemini API está temporariamente indisponível."
        else:
            mensagem = "Ocorreu um erro durante a comunicação com a Gemini API."

        logger.exception("[ETAPA ANÁLISE GEMINI]: Erro da API | HTTP: %s", codigo_status)
        raise GeminiServiceError(mensagem) from exc

    except httpx.TimeoutException as exc:
        logger.exception("[ETAPA ANÁLISE GEMINI]: Tempo limite excedido")
        raise GeminiServiceError("A solicitação excedeu o tempo limite configurado.") from exc

    except (httpx.RequestError, OSError) as exc:
        logger.exception("[ETAPA ANÁLISE GEMINI]: Falha de conexão")
        raise GeminiServiceError("Não foi possível estabelecer comunicação com a Gemini API.") from exc

    except Exception as exc:
        logger.exception("[ETAPA ANÁLISE GEMINI]: Erro inesperado")
        raise GeminiServiceError("Ocorreu um erro inesperado durante a análise dos indicadores.") from exc

    finally:
        if cliente is not None:
            try:
                cliente.close()
                logger.info("[ETAPA ANÁLISE GEMINI]: Cliente encerrado")
            except Exception:
                logger.exception("[ETAPA ANÁLISE GEMINI]: Erro ao encerrar o cliente")
