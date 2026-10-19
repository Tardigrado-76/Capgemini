"""Tests for shared Quantigrade branding and PDF layout engine."""
from __future__ import annotations

import os
import sys

_pkg_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from shared_quantigrade.branding import get_logo_path, get_quantigrade_theme
from shared_quantigrade.pdf_branding import generate_branded_canvas_header


def test_branding_assets() -> None:
    theme = get_quantigrade_theme()
    assert theme["bg_primary"] == "#0a0e17"
    assert theme["accent_blue"] == "#0284c7"
    assert theme["accent_green"] == "#10b981"

    logo = get_logo_path()
    assert os.path.exists(logo)
    assert logo.endswith("Quantigrade.jpg")

def test_branded_canvas_header() -> None:
    # Test that the header helper returns valid dimensions and elements
    header_info = generate_branded_canvas_header(title="Test Executive Document")
    assert header_info["title"] == "Test Executive Document"
    assert header_info["brand"] == "QUANTIGRADE"
    assert "logo_path" in header_info
