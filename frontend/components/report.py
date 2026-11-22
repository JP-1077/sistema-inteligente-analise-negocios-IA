from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from src.services.service_report import report_markdown, report_pdf


def render_report_exportacao(
    dados: pd.DataFrame | None,
    nome_arquivo: str | None = None,
    diagnostico: str | None = None,
) -> None:
    st.subheader("Exportar relatório")
    coluna_pdf, coluna_markdown = st.columns(2)

    relatorio = _montar_relatorio(dados, nome_arquivo, diagnostico)
    if relatorio is None:
        pdf: bytes = b""
        markdown = ""
    else:
        markdown = report_markdown(relatorio)
        pdf = report_pdf(relatorio)

    with coluna_pdf:
        st.download_button(
            "Baixar relatório PDF",
            data=pdf,
            file_name="relatorio-analise.pdf",
            mime="application/pdf",
            disabled=relatorio is None,
            key="download_report_pdf",
        )

    with coluna_markdown:
        st.download_button(
            "Baixar relatório Markdown",
            data=markdown,
            file_name="relatorio-analise.md",
            mime="text/markdown",
            disabled=relatorio is None,
            key="download_report_markdown",
        )


def _montar_relatorio(
    dados: pd.DataFrame | None,
    nome_arquivo: str | None,
    diagnostico: str | None,
) -> dict[str, Any] | None:
    if dados is None or dados.empty:
        return None

    metricas = [
        {"nome": str(coluna)}
        for coluna in dados.select_dtypes(include="number").columns
        if not pd.api.types.is_bool_dtype(dados[coluna])
        and dados[coluna].notna().any()
    ]

    relatorio = {
        "nome_arquivo": nome_arquivo or "Base de dados",
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "analise": {
            "resumo": {
                "total_registros": len(dados),
                "total_colunas": len(dados.columns),
                "metricas_identificadas": len(metricas),
            },
            "metricas_identificadas": metricas,
        },
    }
    if diagnostico:
        relatorio["diagnostico"] = diagnostico

    return relatorio
