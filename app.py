from typing import Final

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from frontend.components import (
    header,
    load_uploaded_dataframe,
    render_data_preview,
    render_file_upload,
    renderizar_painel,
    renderizar_secao_analise,
    renderizar_secao_indicadores,
)
from frontend.styles import load_global_styles


# ---------------------------------------------------------------------------
# Configurações da página
# ---------------------------------------------------------------------------

PAGE_TITLE: Final[str] = "Sistema de Análise de Dados"
PAGE_ICON: Final[str] = "📊"
PAGE_LAYOUT: Final[str] = "wide"
SIDEBAR_INITIAL_STATE: Final[str] = "collapsed"


def configure_page() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT,
        initial_sidebar_state=SIDEBAR_INITIAL_STATE,
    )


# ---------------------------------------------------------------------------
# Seção de upload e prévia
# ---------------------------------------------------------------------------

def render_data_section() -> tuple[
    UploadedFile | None,
    pd.DataFrame | None,
]:
    """Renderiza a seção de upload e pré-visualização dos dados.

    Returns:
        Uma tupla contendo:

        - O arquivo enviado pelo usuário.
        - O DataFrame carregado a partir do arquivo.

        Os valores serão None quando nenhum arquivo tiver sido enviado
        ou quando não for possível realizar sua leitura.
    """
    with st.container(border=True):
        upload_column, preview_column = st.columns(
            spec=[0.8, 2.2],
            gap="large",
            vertical_alignment="top",
        )

        with upload_column:
            uploaded_file = render_file_upload()

        dataframe = load_uploaded_dataframe(uploaded_file)

        with preview_column:
            render_data_preview(
                dataframe=dataframe,
                uploaded_file=uploaded_file,
            )

    return uploaded_file, dataframe

# ---------------------------------------------------------------------------
# Seção de Analytics
# ---------------------------------------------------------------------------

def render_analytics(dados: pd.DataFrame | None, arquivo_enviado: bool) -> None:
    """Renderiza a seção de análise com IA.

    Args:
        dados: DataFrame contendo os dados a serem analisados.
        arquivo_enviado: Indica se um arquivo foi enviado pelo usuário.
    """
    with st.container(border=True):
        st.subheader("Resultado da análise")

        coluna_indicadores, coluna_ia = st.columns([3, 2], gap="large")

        with coluna_indicadores, st.container(border=True):
            renderizar_secao_indicadores(dados=dados, arquivo_enviado=arquivo_enviado)

        with coluna_ia, st.container(border=True):
            renderizar_secao_analise(dados=dados, arquivo_enviado=arquivo_enviado)

# ---------------------------------------------------------------------------
# Seção do dashboard
# ---------------------------------------------------------------------------

def render_dashboard_section(dataframe: pd.DataFrame | None) -> None:
    """Renderiza o dashboard quando houver dados disponíveis.

    Args:
        dataframe:
            DataFrame carregado a partir do arquivo enviado pelo usuário.
    """

    with st.container(border=True):
        st.subheader("Painel de Dashboard")

        if dataframe is None:
            st.warning("Nenhum arquivo carregado. Disponibilize um arquivo para visualizar as análises.")
            return
        
        if dataframe.empty:
            st.warning("O arquivo enviado não contém registros. Verifique o conteúdo e tente novamente.")
            return

        renderizar_painel(dataframe)


# ---------------------------------------------------------------------------
# Orquestração da aplicação
# ---------------------------------------------------------------------------

def main() -> None:
    """Inicializa e coordena a renderização da aplicação."""
    configure_page()
    load_global_styles()

    header()

    uploaded_file, dataframe = render_data_section()

    render_analytics(dados=dataframe, arquivo_enviado=uploaded_file is not None)

    render_dashboard_section(dataframe)



if __name__ == "__main__":
    main()