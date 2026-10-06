
import pandas as pd

class KPIanaliser:
    """
    Responsável pela análise dos KPIs presentes no DataFrame.

    Esta classe realiza a primeira camada de análise dos dados
    antes que eles sejam enviados para a Gemini API.
    """

    LIMITE_VARIACAO_SIGNIFICATIVA = 10.0

    @staticmethod
    def identifica_kpis(df):
        """
        Identifica as colunas numéricas disponíveis no DataFrame.

        KPIs são considerados, inicialmente, as colunas que
        possuem valores numéricos.

        Args:
            df (pd.DataFrame): DataFrame com os dados.

        Returns:
            list: Lista contendo os nomes dos KPIs encontrados.
        """
        if df is None or df.empty:
            return []

        kpis = df.select_dtypes(include="number").columns.tolist()

        return kpis

    @staticmethod
    def calcula_variacao(previous_value, current_value):
        """
        Calcula a variação percentual entre dois valores.

        Fórmula:

            ((valor_atual - valor_anterior) / valor_anterior) * 100

        Args:
            previous_value (float): Valor do período anterior.
            current_value (float): Valor do período atual.

        Returns:
            float: Variação percentual.
        """
        if previous_value is None or current_value is None:
            return None

        if previous_value == 0:
            return None

        variation = (
            (current_value - previous_value)
            / previous_value
        ) * 100

        return round(variation, 2)

    @staticmethod
    def compara_periodos(df, kpi):
        """
        Compara o primeiro e o último valor de um KPI.

        O primeiro registro é tratado como período anterior
        e o último registro como período atual.

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            dict: Informações da comparação.
        """
        if kpi not in df.columns:
            raise ValueError(
                f"O KPI '{kpi}' não existe no DataFrame."
            )

        serie = pd.to_numeric(
            df[kpi],
            errors="coerce"
        ).dropna()

        if len(serie) < 2:
            return {
                "kpi": kpi,
                "previous_value": None,
                "current_value": None,
                "variation": None,
                "status": "Dados insuficientes"
            }

        previous_value = serie.iloc[0]
        current_value = serie.iloc[-1]

        variation = KPIanaliser.calcula_variacao(
            previous_value,
            current_value
        )

        status = KPIanaliser.classifica_variacao(variation)

        return {
            "kpi": kpi,
            "previous_value": previous_value,
            "current_value": current_value,
            "variation": variation,
            "status": status
        }

    @staticmethod
    def calcula_media(df, kpi):
        """
        Calcula a média de um KPI.

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            float: Média do KPI.
        """
        if kpi not in df.columns:
            raise ValueError(
                f"O KPI '{kpi}' não existe no DataFrame."
            )

        serie = pd.to_numeric(
            df[kpi],
            errors="coerce"
        ).dropna()

        if serie.empty:
            return None

        return round(serie.mean(), 2)

    @staticmethod
    def calculate_max(df, kpi):
        """
        Identifica o maior valor de um KPI.

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            float: Maior valor encontrado.
        """
        if kpi not in df.columns:
            raise ValueError(
                f"O KPI '{kpi}' não existe no DataFrame."
            )

        serie = pd.to_numeric(
            df[kpi],
            errors="coerce"
        ).dropna()

        if serie.empty:
            return None

        return serie.max()

    @staticmethod
    def calculate_min(df, kpi):
        """
        Identifica o menor valor de um KPI.

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            float: Menor valor encontrado.
        """
        if kpi not in df.columns:
            raise ValueError(
                f"O KPI '{kpi}' não existe no DataFrame."
            )

        serie = pd.to_numeric(
            df[kpi],
            errors="coerce"
        ).dropna()

        if serie.empty:
            return None

        return serie.min()

    @staticmethod
    def detecta_declinio(df, kpi):
        """
        Detecta se um KPI apresentou uma queda significativa.

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            bool: True caso exista queda significativa.
        """
        comparison = KPIanaliser.compara_periodos(df, kpi)

        variation = comparison["variation"]

        if variation is None:
            return False

        return variation <= -KPIanaliser.LIMITE_VARIACAO_SIGNIFICATIVA

    @staticmethod
    def detecta_crescimento(df, kpi):
        """
        Detecta se um KPI apresentou crescimento significativo.

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            bool: True caso exista crescimento significativo.
        """
        comparison = KPIanaliser.compara_periodos(df, kpi)

        variation = comparison["variation"]

        if variation is None:
            return False

        return variation >= KPIanaliser.LIMITE_VARIACAO_SIGNIFICATIVA

    @staticmethod
    def detecta_trend(df, kpi):
        """
        Identifica a tendência básica de um KPI.

        Retornos possíveis:

            crescimento
            queda
            estabilidade
            dados_insuficientes

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            str: Tendência identificada.
        """
        if kpi not in df.columns:
            raise ValueError(
                f"O KPI '{kpi}' não existe no DataFrame."
            )

        serie = pd.to_numeric(
            df[kpi],
            errors="coerce"
        ).dropna()

        if len(serie) < 2:
            return "dados_insuficientes"

        primeira_metade = serie.iloc[:len(serie) // 2].mean()
        segunda_metade = serie.iloc[len(serie) // 2:].mean()

        variation = KPIanaliser.calcula_variacao(
            primeira_metade,
            segunda_metade
        )

        if variation is None:
            return "dados_insuficientes"

        if variation >= KPIanaliser.LIMITE_VARIACAO_SIGNIFICATIVA:
            return "crescimento"

        if variation <= -KPIanaliser.LIMITE_VARIACAO_SIGNIFICATIVA:
            return "queda"

        return "estabilidade"

    @staticmethod
    def detecta_anomalia(df, kpi):
        """
        Identifica possíveis valores anômalos utilizando
        o desvio padrão.

        Um valor é considerado potencialmente anômalo quando
        está a mais de dois desvios padrão da média.

        Args:
            df (pd.DataFrame): DataFrame com os dados.
            kpi (str): Nome do KPI.

        Returns:
            list: Lista dos valores considerados anômalos.
        """
        if kpi not in df.columns:
            raise ValueError(
                f"O KPI '{kpi}' não existe no DataFrame."
            )

        serie = pd.to_numeric(
            df[kpi],
            errors="coerce"
        ).dropna()

        if len(serie) < 3:
            return []

        media = serie.mean()
        desvio_padrao = serie.std()

        if desvio_padrao == 0:
            return []

        limite_superior = media + (2 * desvio_padrao)
        limite_inferior = media - (2 * desvio_padrao)

        anomalias = serie[
            (serie > limite_superior) |
            (serie < limite_inferior)
        ]

        return anomalias.tolist()

    @staticmethod
    def classifica_variacao(variation):
        """
        Classifica a variação de um KPI.
        """
        if variation is None:
            return "Dados insuficientes"

        if variation <= -KPIanaliser.LIMITE_VARIACAO_SIGNIFICATIVA:
            return "Queda significativa"

        if variation >= KPIanaliser.LIMITE_VARIACAO_SIGNIFICATIVA:
            return "Crescimento significativo"

        return "Estável"

    @staticmethod
    def analise(df):
        """
        Executa a análise completa dos KPIs encontrados.

        Args:
            df (pd.DataFrame): DataFrame recebido do DataService.

        Returns:
            dict: Resultado completo da análise.
        """
        if df is None or df.empty:
            raise ValueError(
                "Não existem dados para realizar a análise."
            )

        kpis = KPIanaliser.identifica_kpis(df)

        if not kpis:
            raise ValueError(
                "Nenhum KPI numérico foi encontrado no arquivo."
            )

        analysis = {
            "total_registros": len(df),
            "total_kpis": len(kpis),
            "kpis": {}
        }

        for kpi in kpis:
            comparison = KPIanaliser.compara_periodos(
                df,
                kpi
            )

            analysis["kpis"][kpi] = {
                "previous_value": comparison["previous_value"],
                "current_value": comparison["current_value"],
                "variation": comparison["variation"],
                "status": comparison["status"],
                "average": KPIanaliser.calcula_media(
                    df,
                    kpi
                ),
                "maximum": KPIanaliser.calculate_max(
                    df,
                    kpi
                ),
                "minimum": KPIanaliser.calculate_min(
                    df,
                    kpi
                ),
                "trend": KPIanaliser.detecta_trend(
                    df,
                    kpi
                ),
                "decline": KPIanaliser.detecta_declinio(
                    df,
                    kpi
                ),
                "growth": KPIanaliser.detecta_crescimento(
                    df,
                    kpi
                ),
                "anomalies": KPIanaliser.detecta_anomalia(
                    df,
                    kpi
                )
            }

        return analysis
