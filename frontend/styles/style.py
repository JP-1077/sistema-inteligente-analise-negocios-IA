"""Carregamento dos estilos globais da aplicação."""

from pathlib import Path
from typing import Final

import streamlit as st


CSS_FILE: Final[Path] = Path(__file__).resolve().parent / "main.css"


def load_global_styles() -> None:
    """Carrega e injeta os estilos globais na aplicação Streamlit."""
    if not CSS_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo de estilos não encontrado: {CSS_FILE}"
        )

    css_content = CSS_FILE.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True,
    )