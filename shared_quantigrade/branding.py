"""Shared Quantigrade Branding & UI Tokens Engine.

Conforms to /ui-ux-pro-max and /brand:
- Cybernetic dark theme (#0a0e17)
- Quantigrade signature blue (#0284c7) and emerald (#10b981)
- Seamless Streamlit layout injection
"""
from __future__ import annotations

import os
from typing import Any

LOGO_PATH = os.path.abspath(r"e:\PROYECTOS IA\Quantigrade.jpg")


def get_logo_path() -> str:
    """Returns absolute verified path to Quantigrade corporate logo."""
    return LOGO_PATH


def get_quantigrade_theme() -> dict[str, str]:
    """Returns standardized Quantigrade UI design tokens."""
    return {
        "bg_primary": "#0a0e17",
        "bg_secondary": "#111827",
        "card_bg": "rgba(18, 25, 41, 0.7)",
        "accent_blue": "#0284c7",
        "accent_green": "#10b981",
        "accent_amber": "#f59e0b",
        "accent_red": "#ef4444",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "border": "rgba(56, 189, 248, 0.2)",
    }


def inject_quantigrade_css(st_module: Any) -> None:
    """Injects executive cybernetic theme CSS into active Streamlit instance."""
    theme = get_quantigrade_theme()
    st_module.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}

        code, pre {{
            font-family: 'JetBrains Mono', monospace !important;
        }}

        .stApp {{
            background: radial-gradient(circle at 10% 10%, #0d1222 0%, {theme['bg_primary']} 100%);
            color: {theme['text_primary']};
        }}

        .metric-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid {theme['border']};
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.3);
            margin-bottom: 12px;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: {theme['bg_secondary']};
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 6px;
            color: {theme['text_secondary']};
            padding: 8px 16px;
            font-weight: 600;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {theme['accent_blue']} !important;
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
