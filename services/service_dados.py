import pandas as pd


class ServiceDados:
    """
    Service responsável pelo processamento e validação
    dos arquivos enviados para a aplicação.
    """

    extensoes_aceitas = [".csv", ".xlsx", ".xls"]

    @staticmethod
    def leitura_csv(file):
        """
        Lê um arquivo CSV e retorna um DataFrame do pandas.
        """
        try:
            df = pd.read_csv(file)
            return df
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo CSV: {e}")

    @staticmethod
    def leitura_excel(file):
        try:
            df = pd.read_excel(file)
            return df
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo Excel: {e}")

    @staticmethod
    def validacao_extensao(file):
        if file is None:
            raise ValueError("Nenhum arquivo foi enviado.")

        nome_arquivo = file.name.lower()

        extensao = None

        for extensao_aceita in ServiceDados.extensoes_aceitas:
            if nome_arquivo.endswith(extensao_aceita):
                extensao = extensao_aceita
                break

        if extensao is None:
            raise ValueError(
                f"Extensão de arquivo inválida. Formatos aceitos: {', '.join(ServiceDados.extensoes_aceitas)}")

        return True

    @staticmethod
    def validar_dataframe(df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Não foi possível carregar os dados do arquivo.")

        if df.empty or len(df.columns) == 0:
            raise ValueError("O arquivo não possui dados para exibir.")

    @staticmethod
    def leitura_arquivo(file):
        ServiceDados.validacao_extensao(file)

        nome_arquivo = file.name.lower()

        if nome_arquivo.endswith(".csv"):
            df = ServiceDados.leitura_csv(file)

        elif nome_arquivo.endswith((".xlsx", ".xls")):
            df = ServiceDados.leitura_excel(file)

        else:
            raise ValueError("Formato de arquivo não suportado.")

        ServiceDados.validar_dataframe(df)

        return df
