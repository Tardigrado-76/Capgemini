"""
Sample Regulatory PDF Generator for Ground Truth Testing.
Generates an authentic normative PDF covering DORA, NIS2 and ENS mandates using ReportLab.
"""

from __future__ import annotations

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
)


def generate_sample_regulatory_pdf(output_path: str) -> str:
    """Compiles a realistic European regulatory PDF document."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "RegTitle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    art_title = ParagraphStyle(
        "ArtTitle",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0284c7"),
        spaceBefore=12,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "RegBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )

    story = [
        Paragraph("DIARIO OFICIAL DE LA UNIÓN EUROPEA — REGLAMENTO (UE) 2022/2554 (DORA & NIS2)", title_style),
        Paragraph("Marco Normativo de Resiliencia Operativa Digital del Sector Financiero e Infraestructuras Críticas", body),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=12),

        Paragraph("Artículo 11: Planes de Continuidad de las TIC y Recuperación ante Desastres", art_title),
        Paragraph(
            "1. Las entidades financieras deberán establecer, mantener y poner a prueba planes adecuados de continuidad de las TIC "
            "que garanticen la preservación de las funciones esenciales.", body,
        ),
        Paragraph(
            "2. El tiempo de recuperación RTO no deberá superar en ningún caso el límite máximo de 2 horas para los servicios esenciales de pago y liquidación.", body,
        ),
        Paragraph(
            "3. Se deberán realizar pruebas periódicas de failover y contingencia multi-región para validar la resiliencia operativa.", body,
        ),

        Paragraph("Artículo 19: Notificación Obligatoria de Incidentes Graves de Ciberseguridad", art_title),
        Paragraph(
            "1. Las entidades sujetas deberán notificar a la autoridad competente y al CSIRT nacional los incidentes graves en un plazo máximo de 24 horas tras su detección.", body,
        ),
        Paragraph(
            "2. Deberán registrar de forma inmutable todas las trazas periciales y registros de auditoría durante al menos doce meses.", body,
        ),

        Paragraph("Artículo 28: Gestión del Riesgo Relacionado con Terceros Prestadores de Servicios de TIC", art_title),
        Paragraph(
            "1. Las entidades deberán evaluar de manera continua los riesgos derivados de la subcontratación de funciones críticas o importantes.", body,
        ),
        Paragraph(
            "2. Todos los datos confidenciales deberán protegerse mediante cifrado obligatorio en reposo y en tránsito empleando algoritmos robustos reconocidos.", body,
        ),

        Paragraph("Artículo 30: Supervisión Humana y Medidas de Gobernanza en Sistemas Autónomos", art_title),
        Paragraph(
            "1. En todo sistema automatizado de toma de decisiones o agente autónomo, se garantizará la supervisión humana (HITL) activa con regla de 4 ojos.", body,
        ),
        Paragraph(
            "2. Queda expresamente prohibida la ejecución de transferencias o acciones críticas sin autorización previa documentada.", body,
        ),
    ]

    doc.build(story)
    return os.path.abspath(output_path)
