import streamlit as st



def header():
    titulo = "Sistema inteligente análise de negócios (Desenvolvimento Software + IA) 📊"
    descrição = "Analise seus indicadores de negócio com o apoio da inteligência artificial."
    label = "João Pedro Mendes Fonseca | Desenvolvedor Software"

    st.markdown(
        f"""
        <header class="app-header">
            <div>
                <h1 class="app-title">{titulo}</h1>
                <p class="app-description">{descrição}</p>
            </div>

            <span class="stage-badge">{label}</span>
        </header>
        """,
        unsafe_allow_html=True
    )
