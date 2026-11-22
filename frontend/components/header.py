import streamlit as st
import html
from textwrap import dedent


def header():
    titulo = "Sistema Análise de Dados"
    descrição = "Analise seus indicadores de negócio de forma mais rápida e eficiente."
    label = "João Pedro Mendes Fonseca Software Developer"

    conteudo = dedent(
        f"""
        <header class="app-header">
            <div>
                <h1 class="app-title">{html.escape(titulo)}</h1>
                <p class="app-description">{html.escape(descrição)}</p>
            </div>
            <span class="stage-badge">{html.escape(label)}</span>
        </header>
        """)

    st.markdown(conteudo, unsafe_allow_html=True)
