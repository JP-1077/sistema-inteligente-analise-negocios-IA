from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

def report_markdown(relatorio: dict) -> str:

    resumo = relatorio["analise"]["resumo"]
    metricas = relatorio["analise"]["metricas_identificadas"]

    linhas = [
        "# Relatório de Análise",
        "",
        f"**Arquivo:** {relatorio['nome_arquivo']}",
        f"**Data:** {relatorio['data_geracao']}",
        "",
        "## Resumo",
        f"- Registros: {resumo['total_registros']}",
        f"- Colunas: {resumo['total_colunas']}",
        f"- Indicadores: {resumo['metricas_identificadas']}",
        "",
        "## Indicadores",
    ]

    linhas.extend(f"- {metrica['nome']}" for metrica in metricas)

    if relatorio.get("diagnostico"):
        linhas.extend([
            "",
            "## Diagnóstico",
            relatorio["diagnostico"],
        ])


    return "\n".join(linhas)


def report_pdf(relatorio: dict) -> bytes:
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    estilos = getSampleStyleSheet()
    conteudo = []

    conteudo.append(
        Paragraph("Relatório de Análise", estilos["Title"])
    )

    conteudo.append(Spacer(1, 8))
    conteudo.append(
        Paragraph(
            f"<b>Arquivo:</b> {escape(str(relatorio['nome_arquivo']))}",
            estilos["Normal"],
        )
    )
    conteudo.append(
        Paragraph(
            f"<b>Data:</b> {escape(str(relatorio['data_geracao']))}",
            estilos["Normal"],
        )
    )

    resumo = relatorio["analise"]["resumo"]

    conteudo.append(Spacer(1, 12))
    conteudo.append(
        Paragraph("Resumo", estilos["Heading2"])
    )
    conteudo.append(
        Paragraph(
            f"Registros: {resumo['total_registros']}<br/>"
            f"Colunas: {resumo['total_colunas']}<br/>"
            f"Indicadores: {resumo['metricas_identificadas']}",
            estilos["Normal"],
        )
    )

    conteudo.append(Spacer(1, 12))
    conteudo.append(
        Paragraph("Indicadores", estilos["Heading2"])
    )

    metricas = relatorio["analise"]["metricas_identificadas"]

    if metricas:
        tabela_indicadores = [["Indicador"]]

        for metrica in metricas:
            tabela_indicadores.append([
                escape(str(metrica["nome"]))
            ])

        tabela = Table(tabela_indicadores, colWidths=[160 * mm])
        tabela.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        conteudo.append(tabela)
    else:
        conteudo.append(
            Paragraph(
                "Nenhum indicador foi identificado.",
                estilos["Normal"],
            )
        )

    diagnostico = relatorio.get("diagnostico")

    if diagnostico:
        conteudo.append(Spacer(1, 12))
        conteudo.append(
            Paragraph("Diagnóstico", estilos["Heading2"])
        )

        texto_diagnostico = escape(str(diagnostico)).replace(
            "\n",
            "<br/>",
        )
        conteudo.append(
            Paragraph(
                texto_diagnostico,
                estilos["Normal"],
            )
        )

    documento.build(conteudo)
    return buffer.getvalue()