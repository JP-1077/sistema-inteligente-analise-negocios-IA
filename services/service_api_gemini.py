import os
from dotenv import load_dotenv
from google import genai


class ServiceApiGemini:

    """Service responsável por enviar prompts para a API Gemini"""

    modelo_padrao = "gemini-2.5-flash"

    def __init__(self, api_key=None, model=None):
        load_dotenv()
        chave_api = api_key or os.getenv("CHAVE_API")
        self.model = model or os.getenv("NOME_API") or self.modelo_padrao

        if not chave_api:
            raise ValueError("A chave da API não foi fornecida. Por favor, defina a variável de ambiente 'CHAVE_API' ou forneça a chave diretamente.")

        self.client = genai.Client(api_key=chave_api)

    def envio_diagnostico(self, prompt):

        if not prompt:
            raise ValueError("O prompt não pode ser vazio. Por favor, forneça um prompt válido.")

        response = self.client.models.generate_content(model=self.model, contents=prompt,)
        diagnostico = response.text

        if not diagnostico or not diagnostico.strip():
            raise ValueError("A Gemini API não retornou um diagnóstico válido.")

        return diagnostico.strip()
