import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile


SUPPORTED_FILE_TYPES = ["csv", "xlsx", "xls"]


def render_file_upload() -> UploadedFile | None:
    """Renderiza o componente responsável pelo upload do arquivo."""
    st.markdown(
        '<p class="section-heading">Carregue sua base de dados abaixo</p>',
        unsafe_allow_html=True,
    )

    st.caption("A partir do upload da base o sistema irá analisar e retornar o resultado")

    return st.file_uploader(
        "Selecionar arquivo",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=False,
        help="Formatos aceitos: CSV, XLSX e XLS.",
    )