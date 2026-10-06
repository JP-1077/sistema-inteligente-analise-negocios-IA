from pathlib import Path

import pandas as pd
import streamlit as st

from prompts.prompt import criar_prompt_diagnostico
from services.service_api_gemini import ServiceApiGemini
from services.service_analytics import KPIanaliser
from services.service_dados import ServiceDados


st.set_page_config(
    page_title="KPI Business Analyzer",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top, rgba(15, 23, 42, 0.95), transparent 42%),
            #020617;
        color: #e5e7eb;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1920px;
        padding: 2rem clamp(1rem, 3vw, 3.5rem) 3rem;
    }

    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        padding: 0 0 1.5rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #1e293b;
    }

    .app-title {
        margin: 0;
        color: #e5e7eb;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .app-description {
        margin: 0.45rem 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }

    .stage-badge {
        flex-shrink: 0;
        padding: 0.4rem 0.75rem;
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 999px;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        font-size: 0.75rem;
        font-weight: 600;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(22, 24, 39, 0.92);
        border-color: #3b3d4b;
        border-radius: 12px;
    }

    .section-heading {
        margin: 0 0 1rem;
        color: #e5e7eb;
        font-size: 1.05rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #334155;
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.55);
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #38bdf8;
    }

    [data-testid="stButton"] > button {
        min-height: 2.8rem;
        border: 0;
        border-radius: 9px;
        background: #0284c7;
        color: #fff;
        font-weight: 600;
        transition: background 150ms ease;
    }

    [data-testid="stButton"] > button:hover {
        border: 0;
        background: #0ea5e9;
        color: #fff;
    }

    @media (max-width: 600px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1.5rem 0.75rem;
        }

        .app-header {
            flex-direction: column;
        }

        .app-title {
            font-size: 1.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <header class="app-header">
        <div>
            <h1 class="app-title">📊 KPI Business Analyzer</h1>
            <p class="app-description">
                Analise seus indicadores de negócio com o apoio da inteligência artificial.
            </p>
        </div>
        <span class="stage-badge">MVP · Etapa 5</span>
    </header>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    upload_column, preview_column = st.columns(
        [0.8, 2.2],
        gap="large",
        vertical_alignment="top",
    )

    with upload_column:
        st.markdown(
            '<p class="section-heading">Dados da sua base</p>',
            unsafe_allow_html=True,
        )
        st.caption("Carregue os indicadores que deseja acompanhar.")
        uploaded_file = st.file_uploader(
            "📁 Selecionar arquivo",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=False,
            help="Formatos aceitos: CSV, XLSX e XLS.",
        )

    with preview_column:
        st.markdown(
            '<p class="section-heading">Prévia dos dados</p>',
            unsafe_allow_html=True,
        )
        if uploaded_file is None:
            st.info("Envie um arquivo para visualizar os dados da base.")
            dataframe = None
        else:
            try:
                dataframe = ServiceDados.leitura_arquivo(uploaded_file)
            except ValueError as error:
                dataframe = None
                st.error(str(error))
            else:
                dataframe.columns = dataframe.columns.map(str)
                st.caption(f"Arquivo: **{uploaded_file.name}**")
                metric_columns = st.columns(3)
                metric_columns[0].metric(
                    "Registros", f"{len(dataframe):,}".replace(",", ".")
                )
                metric_columns[1].metric("Colunas", len(dataframe.columns))
                metric_columns[2].metric(
                    "Tamanho", f"{uploaded_file.size / 1024:.1f} KB"
                )
                st.caption(
                    f"Formato: {Path(uploaded_file.name).suffix.upper().lstrip('.')}"
                )

                st.caption("Colunas identificadas")
                st.write(" · ".join(str(column) for column in dataframe.columns))
                st.dataframe(
                    dataframe.head(10),
                    width="stretch",
                    hide_index=True,
                )
                if len(dataframe) > 10:
                    st.caption("Exibindo as 10 primeiras linhas.")

analyze_clicked = False
if uploaded_file is not None and dataframe is not None:
    with st.container(border=True):
        st.markdown(
            '<p class="section-heading">Dashboard dos dados</p>',
            unsafe_allow_html=True,
        )
        numeric_columns = list(dataframe.select_dtypes(include="number").columns)
        for column in dataframe.columns:
            if column in numeric_columns:
                continue
            converted = pd.to_numeric(dataframe[column], errors="coerce")
            non_empty_values = dataframe[column].notna().sum()
            if (
                non_empty_values > 0
                and converted.notna().sum() / non_empty_values >= 0.8
            ):
                dataframe[column] = converted
                numeric_columns.append(column)

        if not numeric_columns:
            st.warning("Não foram encontradas colunas numéricas para gerar gráficos.")
        else:
            numeric_columns = [str(column) for column in numeric_columns]
            controls = st.columns([1, 1, 2])
            selected_metric = controls[0].selectbox(
                "Indicador principal",
                options=numeric_columns,
                key="dashboard_metric",
            )

            temporal_columns = []
            parsed_dates = {}
            date_name_hints = (
                "data",
                "date",
                "mes",
                "month",
                "periodo",
                "período",
            )
            for column in dataframe.columns:
                is_datetime = pd.api.types.is_datetime64_any_dtype(dataframe[column])
                name_suggests_date = any(
                    hint in str(column).lower() for hint in date_name_hints
                )
                is_numeric = pd.api.types.is_numeric_dtype(dataframe[column])
                if is_datetime or (name_suggests_date and not is_numeric):
                    converted_dates = pd.to_datetime(
                        dataframe[column],
                        errors="coerce",
                        dayfirst=True,
                    )
                    if converted_dates.notna().sum() >= max(
                        1, int(len(dataframe) * 0.8)
                    ):
                        temporal_columns.append(str(column))
                        parsed_dates[str(column)] = converted_dates

            categorical_columns = [
                str(column)
                for column in dataframe.columns
                if str(column) not in numeric_columns
                and str(column) not in temporal_columns
            ]
            selected_date = None
            if temporal_columns:
                selected_date = controls[1].selectbox(
                    "Eixo temporal",
                    options=temporal_columns,
                    key="dashboard_date_axis",
                )
            else:
                controls[1].caption("Sem coluna de data: tendência por ordem dos registros.")

            selected_category = None
            if categorical_columns:
                selected_category = controls[2].selectbox(
                    "Agrupar por categoria",
                    options=categorical_columns,
                    key="dashboard_category",
                )
            else:
                controls[2].caption(
                    "Sem categorias disponíveis: serão mostrados os maiores registros."
                )

            metric_values = pd.to_numeric(dataframe[selected_metric], errors="coerce")
            if not metric_values.notna().any():
                st.warning(f"A coluna {selected_metric} não contém valores numéricos.")
            else:
                average_value = metric_values.mean()
                average_label = (
                    f"{average_value:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                    if pd.notna(average_value)
                    else "—"
                )
                metric_cards = st.columns(3)
                metric_cards[0].metric(
                    "Registros",
                    f"{len(dataframe):,}".replace(",", "."),
                )
                metric_cards[1].metric(f"Média de {selected_metric}", average_label)
                metric_cards[2].metric(
                    "Indicadores numéricos",
                    len(numeric_columns),
                )

                chart_row_one = st.columns(2, gap="large")
                with chart_row_one[0]:
                    st.markdown(f"##### Evolução de {selected_metric}")
                    if selected_date is not None:
                        trend_data = pd.DataFrame(
                            {
                                "Data": parsed_dates[selected_date],
                                selected_metric: metric_values,
                            }
                        ).dropna()
                        trend_data = (
                            trend_data.groupby("Data", as_index=False)[selected_metric]
                            .mean()
                            .sort_values("Data")
                            .head(1000)
                        )
                        st.line_chart(
                            trend_data,
                            x="Data",
                            y=selected_metric,
                            height=340,
                            width="stretch",
                        )
                    else:
                        trend_data = pd.DataFrame(
                            {
                                "Registro": range(1, len(dataframe) + 1),
                                selected_metric: metric_values.to_numpy(),
                            }
                        ).dropna(subset=[selected_metric]).head(1000)
                        st.line_chart(
                            trend_data,
                            x="Registro",
                            y=selected_metric,
                            height=340,
                            width="stretch",
                        )

                with chart_row_one[1]:
                    st.markdown(f"##### {selected_metric} por grupo")
                    if selected_category is not None:
                        category_data = pd.DataFrame(
                            {
                                "Categoria": dataframe[selected_category].astype(str),
                                selected_metric: metric_values,
                            }
                        ).dropna(subset=[selected_metric])
                        category_data = (
                            category_data.groupby("Categoria", as_index=False)[
                                selected_metric
                            ]
                            .mean()
                            .nlargest(15, selected_metric)
                        )
                        st.bar_chart(
                            category_data,
                            x="Categoria",
                            y=selected_metric,
                            height=340,
                            width="stretch",
                        )
                        if dataframe[selected_category].nunique() > 15:
                            st.caption("Exibindo os 15 grupos com maior média.")
                    else:
                        top_records = pd.DataFrame(
                            {
                                "Registro": metric_values.index.astype(str),
                                selected_metric: metric_values,
                            }
                        ).dropna(subset=[selected_metric])
                        top_records = top_records.nlargest(15, selected_metric)
                        st.bar_chart(
                            top_records,
                            x="Registro",
                            y=selected_metric,
                            height=340,
                            width="stretch",
                        )
                        st.caption("15 registros com os maiores valores.")

                chart_row_two = st.columns(2, gap="large")
                with chart_row_two[0]:
                    st.markdown(f"##### Distribuição de {selected_metric}")
                    distribution_values = metric_values.dropna()
                    bin_count = min(12, max(1, distribution_values.nunique()))
                    bins = pd.cut(distribution_values, bins=bin_count)
                    distribution_data = (
                        bins.value_counts(sort=False)
                        .rename_axis("Faixa")
                        .reset_index(name="Registros")
                    )
                    distribution_data["Faixa"] = distribution_data["Faixa"].astype(str)
                    st.bar_chart(
                        distribution_data,
                        x="Faixa",
                        y="Registros",
                        height=340,
                        width="stretch",
                    )

                with chart_row_two[1]:
                    other_metrics = [
                        column for column in numeric_columns if column != selected_metric
                    ]
                    if other_metrics:
                        comparison_metric = st.selectbox(
                            "Comparar com",
                            options=other_metrics,
                            key="dashboard_comparison_metric",
                        )
                        st.markdown(
                            f"##### Relação entre {selected_metric} e {comparison_metric}"
                        )
                        comparison_data = pd.DataFrame(
                            {
                                selected_metric: metric_values,
                                comparison_metric: pd.to_numeric(
                                    dataframe[comparison_metric],
                                    errors="coerce",
                                ),
                            }
                        ).dropna()
                        st.scatter_chart(
                            comparison_data,
                            x=selected_metric,
                            y=comparison_metric,
                            height=340,
                            width="stretch",
                        )
                    else:
                        st.markdown(f"##### Resumo de {selected_metric}")
                        statistics = metric_values.agg(
                            ["min", "median", "mean", "max"]
                        )
                        statistics_data = pd.DataFrame(
                            {
                                "Estatística": [
                                    "Mínimo",
                                    "Mediana",
                                    "Média",
                                    "Máximo",
                                ],
                                "Valor": [
                                    statistics["min"],
                                    statistics["median"],
                                    statistics["mean"],
                                    statistics["max"],
                                ],
                            }
                        )
                        st.bar_chart(
                            statistics_data,
                            x="Estatística",
                            y="Valor",
                            height=340,
                            width="stretch",
                        )

with st.container():
    button_column, _ = st.columns([1, 3])
    with button_column:
        analyze_clicked = st.button(
            "🔍 Analisar indicadores com IA",
            type="primary",
            width="stretch",
        )

st.subheader("Resultado da análise")

if analyze_clicked:
    if uploaded_file is None:
        st.warning("Envie um arquivo CSV ou Excel antes de iniciar a análise.")
    elif dataframe is None:
        st.warning("Corrija o arquivo enviado antes de iniciar a análise.")
    else:
        try:
            analise = KPIanaliser.analise(dataframe)
        except ValueError as error:
            st.error(str(error))
        else:
            resumo_kpis = [
                {
                    "KPI": nome,
                    "Valor anterior": dados["previous_value"],
                    "Valor atual": dados["current_value"],
                    "Variação (%)": dados["variation"],
                    "Status": dados["status"],
                    "Tendência": dados["trend"],
                }
                for nome, dados in analise["kpis"].items()
            ]
            st.markdown("#### Indicadores identificados")
            st.dataframe(resumo_kpis, width="stretch", hide_index=True)

            try:
                prompt = criar_prompt_diagnostico(analise)
                with st.spinner("Analisando os indicadores com a Gemini API..."):
                    diagnostico = ServiceApiGemini().envio_diagnostico(prompt)
            except Exception as error:
                st.error(f"Não foi possível gerar o diagnóstico: {error}")
            else:
                st.markdown("#### Diagnóstico Gemini")
                st.markdown(diagnostico)
else:
    st.info(
        "Os resultados aparecerão aqui depois que você enviar um arquivo "
        "e clicar em **Analisar indicadores**."
    )
