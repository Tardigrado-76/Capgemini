"""
Test suite for launchers, port assignments, and workspace integrity.
Ensures zero port collisions across the entire Quantigrade ecosystem.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT_DIR = Path(r"E:\PROYECTOS IA")
NEW_TOOLS_DIR = ROOT_DIR / "NEW TOOLS"


def _resolve_service_dir(dir_name: str) -> Path:
    variations = [dir_name]
    if dir_name.startswith("IWAN - "):
        variations.append(dir_name[7:])
    else:
        variations.append(f"IWAN - {dir_name}")

    base_dirs = [
        Path(__file__).resolve().parent.parent.parent,
        ROOT_DIR / "NEW TOOLS" / "CAPGEMINI",
        ROOT_DIR / "NEW TOOLS",
    ]
    for base in base_dirs:
        for v in variations:
            candidate = base / v
            if candidate.exists():
                return candidate
    return base_dirs[0] / dir_name


SERVICES = [
    {
        "id": "maestro",
        "name": "Quantigrade Maestro Cockpit",
        "dir": _resolve_service_dir("QGRADE_OS Iwan reference"),
        "bat": "INICIAR_QUANTIGRADE_MAESTRO.bat",
        "app_file": "app_quantigrade_maestro.py",
        "expected_port": 8500,
    },
    {
        "id": "cfo",
        "name": "Autonomous CFO",
        "dir": _resolve_service_dir("IWAN - CFO Director Financiero Autónomo para PYMEs PoC Purgatory"),
        "bat": "INICIAR_CFO_AUTONOMO.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8501,
    },
    {
        "id": "workforce",
        "name": "Workforce AI Hub",
        "dir": _resolve_service_dir("WORKFORCE AI HUB (Upwork de Empleados de IA Autónomos a demanda)"),
        "bat": "INICIAR_WORKFORCE_AI.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8502,
    },
    {
        "id": "outbound",
        "name": "Outbound Machine",
        "dir": _resolve_service_dir("OUTBOUND MACHINE (Motor B2B Autónomo de Prospección y Cierre)"),
        "bat": "INICIAR_OUTBOUND_MACHINE.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8504,
    },
    {
        "id": "white_coding",
        "name": "White Coding Harness",
        "dir": _resolve_service_dir("IWAN - WHITE CODING HARNESS"),
        "bat": "INICIAR_WHITE_CODING_HARNESS.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8506,
    },
    {
        "id": "compliance",
        "name": "Compliance-as-Code Live Mesh",
        "dir": _resolve_service_dir("IWAN - Compliance-as-Code Live Mesh"),
        "bat": "INICIAR_COMPLIANCE_LIVE_MESH.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8507,
    },
    {
        "id": "omni",
        "name": "Omni Contact Center",
        "dir": _resolve_service_dir("OMNI CONTACT CENTER (Centro Multicanal Autónomo de Soporte y Operaciones)"),
        "bat": "INICIAR_OMNI_CONTACT.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8508,
    },
    {
        "id": "tau",
        "name": "Agent Evaluation Framework - TAU-bench",
        "dir": _resolve_service_dir("IWAN - Agent Evaluation Framework — El TAU-benchGAIA"),
        "bat": "INICIAR_AGENT_EVALUATION.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8509,
    },
    {
        "id": "sdp",
        "name": "Semantic Discovery Protocol",
        "dir": _resolve_service_dir("IWAN - Semantic Discovery Protocol"),
        "bat": "INICIAR_SEMANTIC_DISCOVERY.bat",
        "app_file": "app_streamlit.py",
        "expected_port": 8510,
    },
]


def test_port_allocation_uniqueness():
    """Ensures each service is bound to a unique dedicated port with zero collision."""
    ports = [s["expected_port"] for s in SERVICES]
    assert len(ports) == 9
    assert len(set(ports)) == 9, f"Duplicate ports found: {ports}"


def test_batch_launchers_exist_and_ports_match():
    """Inspects all individual .bat files to ensure they exist and specify their exact assigned port."""
    for s in SERVICES:
        bat_path = s["dir"] / s["bat"]
        assert bat_path.exists(), f"Launcher not found: {bat_path}"

        content = bat_path.read_text(encoding="utf-8", errors="ignore")
        port_match = re.search(r"--server\.port\s+(\d+)", content)
        assert port_match is not None, f"No --server.port found in {bat_path}"

        actual_port = int(port_match.group(1))
        assert actual_port == s["expected_port"], (
            f"Port mismatch in {s['name']}: expected {s['expected_port']}, got {actual_port}"
        )


def test_master_suite_launcher_integrity():
    """Verifies master launcher exists and references all batch scripts."""
    master_bat = ROOT_DIR / "INICIAR_SUITE_QUANTIGRADE_HUB.bat"
    assert master_bat.exists(), f"Master launcher missing at {master_bat}"

    content = master_bat.read_text(encoding="utf-8", errors="ignore")
    # All subordinate engines must be referenced in the master hub
    for s in SERVICES:
        if s["id"] != "maestro":
            assert s["bat"] in content, f"Master launcher does not reference {s['bat']}"


def test_streamlit_app_entrypoints_exist():
    """Ensures Streamlit entrypoint script exists in each module directory."""
    for s in SERVICES:
        app_file = s["dir"] / s["app_file"]
        assert app_file.exists(), f"{s['app_file']} missing in {s['dir']}"
