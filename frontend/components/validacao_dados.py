from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from services.service_dados import ServiceDados


limite_linhas_visualizacao = 10


def load_uploaded_dataframe(uploaded_file: UploadedFile | None) -> pd.DataFrame | None:
    """Lê o arquivo enviado e normaliza os nomes das colunas."""
    if uploaded_file is None:
        return None

    try:
        dataframe = ServiceDados.leitura_arquivo(uploaded_file)
    except ValueError as error:
        st.error(str(error))
        return None

    normalized_dataframe = dataframe.copy()
    normalized_dataframe.columns = normalized_dataframe.columns.map(str)

    return normalized_dataframe


def render_data_preview(dataframe: pd.DataFrame | None, uploaded_file: UploadedFile | None) -> None:
    """Renderiza a prévia e os metadados do arquivo."""
    st.markdown('<p class="section-heading">Prévia dos dados</p>', unsafe_allow_html=True)

    if uploaded_file is None:
        st.info("Envie um arquivo para visualizar os dados da base.")
        return

    if dataframe is None:
        st.warning("Não foi possível gerar a prévia dos dados.")
        return

    st.caption(f"Arquivo: **{uploaded_file.name}**")

    _render_file_metrics(dataframe, uploaded_file)
    _render_file_format(uploaded_file)
    _render_column_summary(dataframe)
    _render_dataframe_sample(dataframe)


def _render_file_metrics(dataframe: pd.DataFrame, uploaded_file: UploadedFile) -> None:
    """Renderiza os principais metadados da base carregada."""
    metric_columns = st.columns(3)

    metric_columns[0].metric("Registros", f"{len(dataframe):,}".replace(",", "."),)

    metric_columns[1].metric("Colunas", len(dataframe.columns),)

    metric_columns[2].metric("Tamanho", f"{uploaded_file.size / 1024:.1f} KB",)


def _render_file_format(uploaded_file: UploadedFile) -> None:
    """Renderiza a extensão do arquivo enviado."""
    extension = Path(uploaded_file.name).suffix.upper().lstrip(".")
    st.caption(f"Formato: {extension}")


def _render_column_summary(dataframe: pd.DataFrame) -> None:
    """Renderiza os nomes das colunas identificadas."""
    st.caption("Colunas identificadas")
    st.write(" · ".join(dataframe.columns))


def _render_dataframe_sample(dataframe: pd.DataFrame, row_limit: int = limite_linhas_visualizacao) -> None:
    """Renderiza uma amostra limitada do DataFrame."""
    st.dataframe(dataframe.head(row_limit), width="stretch", hide_index=True)

    if len(dataframe) > row_limit:
        st.caption(f"Exibindo as {row_limit} primeiras linhas.")