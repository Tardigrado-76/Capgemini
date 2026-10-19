"""PDF Branding & Header Stamping Module for Quantigrade Dossiers.

Provides discrete branding, header logos, and legal watermarks
using ReportLab when available, with graceful fallback.
"""
from __future__ import annotations

import os
from typing import Any

from .branding import get_logo_path


def generate_branded_canvas_header(title: str) -> dict[str, str]:
    """Returns metadata for PDF report generators."""
    return {
        "brand": "QUANTIGRADE",
        "title": title,
        "logo_path": get_logo_path(),
        "tagline": "Autonomous AI Engineering & Regulatory Mesh",
        "confidentiality": "CONFIDENTIAL & PROPRIETARY — QUANTIGRADE",
    }


def draw_quantigrade_header(canvas: Any, doc: Any, title: str = "") -> None:
    """Draws discrete Quantigrade header and logo on ReportLab canvas pages."""
    logo = get_logo_path()
    canvas.saveState()

    try:
        if os.path.exists(logo):
            # Draw logo discretely on top right
            canvas.drawImage(logo, doc.pagesize[0] - 70, doc.pagesize[1] - 45, width=32, height=32, preserveAspectRatio=True, mask="auto")
    except (OSError, ValueError):
        # Graceful fallback if image format has unsupported alpha or dimensions
        pass

    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColorRGB(0.58, 0.64, 0.72)  # #94a3b8
    canvas.drawString(40, doc.pagesize[1] - 30, f"QUANTIGRADE — {title.upper()}" if title else "QUANTIGRADE EXECUTIVE DOSSIER")

    canvas.setFont("Helvetica", 7)
    canvas.setFillColorRGB(0.38, 0.44, 0.52)
    canvas.drawRightString(doc.pagesize[0] - 80, doc.pagesize[1] - 30, "EU AI ACT / NIS2 / DORA AUDITED")

    # Bottom footer with page numbers
    canvas.setFont("Helvetica", 7)
    canvas.drawString(40, 20, "CONFIDENTIAL — STRICTLY FOR AUTHORIZED STAKEHOLDERS")
    canvas.drawRightString(doc.pagesize[0] - 40, 20, f"Page {canvas.getPageNumber()}")

    canvas.restoreState()
