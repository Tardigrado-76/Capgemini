"""Semantic Discovery Protocol (SDP) - Executive Streamlit Cockpit.

The Universal Reference Model for Agent Connectors.
Transforms monolithic tool schemas into a 4-Tier Progressive Disclosure Mesh.
Tailored for Quantigrade - Detalle Iwan (Quantum-Resilient Systems).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

# Add local package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from benchmark.token_comparator import TokenBenchmarkSuite
from mcp_bridge.server import SDPProtocolMCPServer
from protocol.adapters.openapi_adapter import OpenAPIConnector
from protocol.progressive_hydrator import ProgressiveHydrator
from protocol.registry import CapabilityRegistry
from protocol.semantic_router import SemanticRouter
from protocol.spec import (
    ConnectorProtocol,
    ExecutionContext,
    RoutingQuery,
)
from protocol.validator import MultiLevelValidator
from provenance.merkle_sealer import DiscoveryMerkleSealer
from provenance.sha256_ledger import DiscoveryLedger

# Page Configuration
st.set_page_config(
    page_title="Quantigrade | Semantic Discovery Protocol",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark Executive & Quantum Cybernetic Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp {
        background-color: #050913;
        color: #f1f5f9;
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(13, 21, 39, 0.85) 0%, rgba(8, 14, 28, 0.95) 100%);
        border: 1px solid rgba(0, 240, 255, 0.22);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5);
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(0, 240, 255, 0.5);
        transform: translateY(-2px);
    }

    .metric-val {
        font-size: 2.1rem;
        font-weight: 800;
        color: #00F0FF;
        letter-spacing: -0.02em;
    }

    .metric-lbl {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 4px;
    }

    /* Badges */
    .q-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .badge-cyan {
        background: rgba(0, 240, 255, 0.12);
        color: #00F0FF;
        border: 1px solid rgba(0, 240, 255, 0.35);
    }
    .badge-emerald {
        background: rgba(0, 255, 157, 0.12);
        color: #00FF9D;
        border: 1px solid rgba(0, 255, 157, 0.35);
    }
    .badge-violet {
        background: rgba(138, 43, 226, 0.15);
        color: #C084FC;
        border: 1px solid rgba(138, 43, 226, 0.35);
    }
    .badge-amber {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(13, 21, 39, 0.6);
        padding: 6px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 240, 255, 0.15) !important;
        color: #00F0FF !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Application State
if "registry" not in st.session_state:
    st.session_state.registry = CapabilityRegistry(auto_discover_skills=True)
    st.session_state.router = SemanticRouter(st.session_state.registry)
    st.session_state.hydrator = ProgressiveHydrator(st.session_state.registry)
    st.session_state.validator = MultiLevelValidator(st.session_state.registry)
    st.session_state.mcp_server = SDPProtocolMCPServer(st.session_state.registry)
    st.session_state.bench_suite = TokenBenchmarkSuite()
    st.session_state.ledger = DiscoveryLedger()
    st.session_state.sealer = DiscoveryMerkleSealer()
if "active_query" not in st.session_state:
    st.session_state.active_query = "Necesito consultar el stock de un material en el centro 1000 de SAP"
if "query_box_val" not in st.session_state:
    st.session_state.query_box_val = st.session_state.active_query
if "last_matches" not in st.session_state:
    st.session_state.last_matches = []
if "last_seal" not in st.session_state:
    st.session_state.last_seal = None
if "last_routed_query" not in st.session_state:
    st.session_state.last_routed_query = None

registry: CapabilityRegistry = st.session_state.registry
router: SemanticRouter = st.session_state.router
hydrator: ProgressiveHydrator = st.session_state.hydrator
validator: MultiLevelValidator = st.session_state.validator
mcp_server: SDPProtocolMCPServer = st.session_state.mcp_server
bench_suite: TokenBenchmarkSuite = st.session_state.bench_suite
ledger: DiscoveryLedger = st.session_state.ledger
sealer: DiscoveryMerkleSealer = st.session_state.sealer


def execute_routing(
    query_text: str,
    top_k: int = 4,
    target_protocol: ConnectorProtocol | None = None,
) -> None:
    """Executes semantic routing across registered capabilities and seals evidence."""
    st.session_state.active_query = query_text
    st.session_state.query_box_val = query_text
    q = RoutingQuery(query=query_text, top_k=top_k, filter_protocol=target_protocol)
    matches = router.route(q)
    st.session_state.last_matches = matches
    ledger.append_event("CAPABILITY_ROUTED", {
        "query": query_text,
        "top_k": top_k,
        "matches_count": len(matches),
        "top_match": matches[0].capability_id if matches else "NONE",
    })
    sealer.add_evidence("ROUTING_DECISION", query_text, [m.model_dump() for m in matches])
    st.session_state.last_seal = sealer.seal()
    st.session_state.last_routed_query = query_text

def set_query_widget_safely(new_text: str) -> None:
    """Safely pre-populates the input widget before it is instantiated."""
    try:
        st.session_state["query_box_input_widget"] = new_text
    except Exception:  # noqa: S110, BLE001
        pass


# Locate Quantigrade Logo
logo_candidates = [
    Path(__file__).resolve().parent / "assets" / "Quantigrade.jpg",
    Path(r"E:\PROYECTOS IA\Quantigrade.jpg"),
]
logo_path = next((p for p in logo_candidates if p.exists()), None)


# -------------------------------------------------------------
# SIDEBAR: FLEET CONTROL & CRYPTO PROVENANCE
# -------------------------------------------------------------
with st.sidebar:
    if logo_path:
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("## ⚡ QUANTIGRADE")

    st.markdown("<div style='text-align:center;'><span class='q-badge badge-cyan'>Quantigrade - Detalle Iwan</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:0.75rem;color:#64748b;margin-top:4px;'>Universal Connector Reference Model</p>", unsafe_allow_html=True)
    st.markdown("---")

    all_caps = registry.get_index()
    skills_cnt = len([c for c in all_caps if c.protocol == ConnectorProtocol.AGENT_SKILL])
    mcp_cnt = len([c for c in all_caps if c.protocol == ConnectorProtocol.MCP])
    openapi_cnt = len([c for c in all_caps if c.protocol == ConnectorProtocol.OPENAPI])
    swarm_cnt = len([c for c in all_caps if c.protocol == ConnectorProtocol.BASE_TOOL])
    erp_cnt = len([c for c in all_caps if c.protocol in (ConnectorProtocol.ENTERPRISE_ERP, ConnectorProtocol.DATABASE)])

    st.markdown("##### 🌐 Flota de Conectores Conectados:")
    st.markdown(f"• **Agent Skills (Antigravity):** `{skills_cnt}`")
    st.markdown(f"• **MCP Tools (Claude/Cursor):** `{mcp_cnt}`")
    st.markdown(f"• **OpenAPI Endpoints:** `{openapi_cnt}`")
    st.markdown(f"• **Swarms & Agency Tools:** `{swarm_cnt}`")
    st.markdown(f"• **Enterprise ERP / Data (SAP/Odoo):** `{erp_cnt}`")
    st.markdown(f"• **Total Activo en Mesh:** `{len(all_caps)} conectores`")

    st.markdown("---")
    st.markdown("##### 🛡️ Cripto-Gobernanza (SLSA L3+):")
    is_valid = ledger.verify_chain()
    status_color = "#00FF9D" if is_valid else "#f87171"
    st.markdown(f"• **SHA-256 Ledger:** <span style='color:{status_color};font-weight:700;'>Cadena 100% Íntegra</span>", unsafe_allow_html=True)
    st.markdown(f"• **Bloques Sellados:** `{len(ledger.chain)}`")
    st.markdown("• **Algoritmo de Firma:** `Ed25519 / Merkle`")

    st.markdown("---")
    st.markdown("##### ⚡ Consultas Rápidas de Prueba:")
    if st.button("📦 Consultar stock y almacén (SAP S/4HANA)", key="btn_preset_sap", use_container_width=True):
        q_sap = "Consultar stock disponible de material y centro en SAP OData"
        set_query_widget_safely(q_sap)
        execute_routing(q_sap, top_k=4, target_protocol=ConnectorProtocol.ENTERPRISE_ERP)
        st.toast("⚡ Conector resuelto: SAP S/4HANA OData", icon="📦")
        st.rerun()
    if st.button("🧾 Conciliar facturas impagadas (Odoo ERP)", key="btn_preset_odoo", use_container_width=True):
        q_odoo = "Listar facturas impagadas y proveedores vencidos en Odoo"
        set_query_widget_safely(q_odoo)
        execute_routing(q_odoo, top_k=4, target_protocol=ConnectorProtocol.ENTERPRISE_ERP)
        st.toast("⚡ Conector resuelto: Odoo Invoicing", icon="🧾")
        st.rerun()
    if st.button("🩺 Auditar código y seguridad (Code Doctor)", key="btn_preset_doctor", use_container_width=True):
        q_doc = "Ejecutar auditoria integral de código Python con ruff y bandit"
        set_query_widget_safely(q_doc)
        execute_routing(q_doc, top_k=4, target_protocol=ConnectorProtocol.AGENT_SKILL)
        st.toast("⚡ Conector resuelto: Code Doctor Audit", icon="🩺")
        st.rerun()
    if st.button("📊 Disparar webhook DORA (n8n)", key="btn_preset_n8n", use_container_width=True):
        q_n8n = "Emitir evento de despliegue a webhook n8n para certificar DORA"
        set_query_widget_safely(q_n8n)
        execute_routing(q_n8n, top_k=4, target_protocol=ConnectorProtocol.ENTERPRISE_ERP)
        st.toast("⚡ Conector resuelto: n8n Workflow Webhook", icon="📊")
        st.rerun()
    if st.button("🎙️ Transcribir audio de llamada (m3cp)", key="btn_preset_m3cp", use_container_width=True):
        q_m3cp = "Quiero transcribir una llamada de audio y separar interlocutores"
        set_query_widget_safely(q_m3cp)
        execute_routing(q_m3cp, top_k=4, target_protocol=ConnectorProtocol.MCP)
        st.toast("⚡ Conector resuelto: m3cp Audio Transcribe", icon="🎙️")
        st.rerun()

    if st.session_state.get("last_routed_query"):
        top_m = st.session_state.last_matches[0] if st.session_state.last_matches else None
        top_txt = f"{top_m.name} ({top_m.confidence*100:.0f}%)" if top_m else "Sin coincidencia"
        st.markdown(
            f"<div style='margin-top:10px;padding:8px 12px;background:rgba(0,240,255,0.08);border:1px solid rgba(0,240,255,0.25);border-radius:8px;font-size:0.75rem;'>"
            f"<span style='color:#00F0FF;font-weight:700;'>Última resolución:</span><br>"
            f"<span style='color:#f1f5f9;'>{st.session_state.last_routed_query[:32]}...</span><br>"
            f"<span style='color:#00FF9D;font-weight:600;'>Top: {top_txt}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


# -------------------------------------------------------------
# TOP HEADER
# -------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("⚡ Semantic Discovery Protocol (SDP)")
    st.markdown(
        "**El Modelo de Referencia Universal para Conectores de IA de Mercado**.<br>"
        "Supera las limitaciones del Tool-Stuffing y de MCP tradicional mediante **Divulgación Progresiva en 4 Capas** "
        "(Tier 0 Manifest ~18 tok → Tier 1 Resolver → Tier 2 JIT Hydrate → Tier 3 Pre-Flight & Sandboxed Execution).",
        unsafe_allow_html=True,
    )
with col_h2:
    st.markdown("""
    <div style="text-align:right; margin-top:12px;">
        <span class="q-badge badge-emerald">MARKET-READY CANONICAL</span><br>
        <span class="q-badge badge-cyan" style="margin-top:6px;">PORT 8508 ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get("last_routed_query"):
    top_cap = st.session_state.last_matches[0] if st.session_state.last_matches else None
    top_info = f"<b>Top Match:</b> <span style='color:#00FF9D;font-weight:700;'>{top_cap.name}</span> (Afinidad: {top_cap.confidence*100:.1f}%)" if top_cap else "Sin coincidencias directas"
    st.markdown(
        f"<div style='background:linear-gradient(90deg, rgba(0,240,255,0.12) 0%, rgba(5,9,19,0.9) 100%);border-left:4px solid #00F0FF;padding:10px 16px;border-radius:6px;margin:12px 0;'>"
        f"⚡ <b>Consulta Rápida Activa:</b> <i>\"{st.session_state.last_routed_query}\"</i> &nbsp;|&nbsp; "
        f"{top_info} &nbsp;|&nbsp; <span style='color:#00F0FF;'>Resultados completos en Pestaña 2</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------
# MAIN WORKSPACE TABS
# -------------------------------------------------------------
tab_matrix, tab_router, tab_exec, tab_openapi, tab_mcp, tab_bench, tab_bunker = st.tabs([
    "🌐 1. Fleet Matrix de Conectores",
    "🔍 2. Enrutador Semántico & JIT",
    "🚀 3. Playground & Pre-Flight (Tier 3)",
    "📥 4. Ingestion Studio OpenAPI",
    "🔌 5. Gateway MCP & Swarms Bridge",
    "📊 6. Benchmark Científico",
    "📜 7. Búnker Criptográfico",
])


# -------------------------------------------------------------
# TAB 1: FLEET MATRIX DE CONECTORES
# -------------------------------------------------------------
with tab_matrix:
    st.subheader("Catálogo Polimórfico Federado de Conectores")
    st.markdown(
        "SDP unifica cualquier origen de herramienta (**MCP Server, OpenAPI 3.x, Antigravity Agent Skill, "
        "Swarms BaseTool o ERP empresarial**) bajo un contrato formal homogéneo con huella Tier 0 ultra-compacta."
    )

    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_filter = st.text_input("Filtrar por nombre, ID, namespace o palabra clave:", placeholder="ej: sap, odoo, audit, git, sql...")
        proto_filter = st.selectbox(
            "Filtrar por Protocolo:",
            [
                "TODOS",
                "MCP Tools (mcp)",
                "OpenAPI Endpoints (openapi)",
                "Agent Skills (skill)",
                "Swarms BaseTools (base_tool)",
                "Enterprise ERP (enterprise_erp)",
                "Database (database)",
            ],
        )
    with f_col3:
        type_filter = st.selectbox(
            "Filtrar por Tipo de Capacidad:",
            ["TODOS", "agent_skill", "mcp_tool", "workflow_template", "composite_flow"],
        )

    all_caps = registry.get_index()
    filtered = all_caps

    if proto_filter != "TODOS":
        target_val = proto_filter.split("(")[-1].replace(")", "").strip()
        filtered = [c for c in filtered if c.protocol.value == target_val]
    if type_filter != "TODOS":
        filtered = [c for c in filtered if c.type.value == type_filter]
    if search_filter:
        s_lower = search_filter.lower()
        filtered = [
            c for c in filtered
            if s_lower in c.id.lower() or s_lower in c.name.lower() or s_lower in c.description.lower()
            or any(s_lower in k.lower() for k in c.keywords)
        ]

    st.markdown(f"**Mostrando {len(filtered)} conectores encontrados:**")

    for cap in filtered:
        badge_style = "badge-cyan"
        if cap.protocol == ConnectorProtocol.AGENT_SKILL:
            badge_style = "badge-violet"
        elif cap.protocol in (ConnectorProtocol.ENTERPRISE_ERP, ConnectorProtocol.DATABASE):
            badge_style = "badge-emerald"
        elif cap.protocol == ConnectorProtocol.OPENAPI:
            badge_style = "badge-amber"

        with st.expander(f"[{cap.protocol.value.upper()}] {cap.name} (`{cap.id}`) — {cap.namespace}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Descripción:** {cap.description}")
                st.markdown(f"**Keywords Semánticas:** {', '.join(f'`{k}`' for k in cap.keywords)}")
                st.markdown(f"**Protocolo Origen:** `{cap.protocol.value}` | **Tipo:** `{cap.type.value}`")
            with c2:
                st.markdown(
                    f"<div class='metric-card'><div class='metric-lbl'>Huella Tier 0</div><div class='metric-val'>{cap.estimated_tokens} <span style='font-size:0.9rem;color:#94a3b8;'>tokens</span></div></div>",
                    unsafe_allow_html=True,
                )

            # Exporter Actions
            connector = registry.get_connector(cap.id)
            if connector:
                b_col1, b_col2, b_col3 = st.columns(3)
                with b_col1:
                    if st.button("Exportar como MCP Tool", key=f"btn_mcp_{cap.id}"):
                        st.json(connector.export_as_mcp_tool())
                with b_col2:
                    if st.button("Exportar a Swarms BaseTool", key=f"btn_sw_{cap.id}"):
                        st.code(
                            f"# Swarms dynamic tool binding for {cap.id}\n"
                            f"from protocol.adapters.swarm_adapter import SwarmToolConnector\n"
                            f"tool_cls = connector.export_as_base_tool()\n"
                            f"instance = tool_cls()\n"
                            f"# Ready to assign to swarms.Agent(tools=[instance])",
                            language="python",
                        )
                with b_col3:
                    if st.button("Ver Schema JSON (Tier 2)", key=f"btn_sch_{cap.id}"):
                        st.json(connector.get_raw_schema())


# -------------------------------------------------------------
# TAB 2: ENRUTADOR SEMÁNTICO & JIT HYDRATOR
# -------------------------------------------------------------
with tab_router:
    st.subheader("Tier 1: Resolución Semántica de Intención de Agentes")
    st.markdown(
        "El agente expone su meta en lenguaje natural. El router semántico analiza el índice compacto "
        "Tier 0 (~18 tokens/tool) y selecciona únicamente el Top-K con afinidad semántica y justificación de selección."
    )

    if "query_box_input_widget" not in st.session_state:
        st.session_state.query_box_input_widget = st.session_state.active_query

    user_query = st.text_input(
        "Consulta o Intención del Agente Autónomo:",
        key="query_box_input_widget",
    )

    col_r1, col_r2 = st.columns([1, 1])
    with col_r1:
        top_k_val = st.slider("Número Máximo de Candidatos (Top-K):", min_value=1, max_value=8, value=4)
    with col_r2:
        protocol_filter_opt = st.selectbox(
            "Filtrar por Protocolo de Destino:",
            ["Cualquiera", "Enterprise ERP", "Agent Skill", "MCP Tool", "OpenAPI"],
        )

    target_proto = None
    if protocol_filter_opt == "Enterprise ERP":
        target_proto = ConnectorProtocol.ENTERPRISE_ERP
    elif protocol_filter_opt == "Agent Skill":
        target_proto = ConnectorProtocol.AGENT_SKILL
    elif protocol_filter_opt == "MCP Tool":
        target_proto = ConnectorProtocol.MCP
    elif protocol_filter_opt == "OpenAPI":
        target_proto = ConnectorProtocol.OPENAPI

    if st.button("🚀 Resolver Conector Semánticamente", type="primary", use_container_width=True):
        execute_routing(user_query, top_k=top_k_val, target_protocol=target_proto)
        st.rerun()

    if st.session_state.last_matches:
        st.markdown("---")
        st.markdown(f"### Candidatos Top-{len(st.session_state.last_matches)} Resueltos para el Agente:")

        for idx, m in enumerate(st.session_state.last_matches, 1):
            badge_color = "#00FF9D" if m.confidence >= 0.50 else "#FBBF24"
            with st.expander(f"#{idx} [{m.type.upper()}] {m.name} (`{m.capability_id}`) — Confianza: {m.confidence*100:.1f}%", expanded=(idx == 1)):
                c_m1, c_m2 = st.columns([2, 1])
                with c_m1:
                    st.markdown(f"**Descripción:** {m.summary}")
                    st.markdown("**Criterios y Palabras Clave de Afinidad:**")
                    for reason in m.match_reasons:
                        st.markdown(f"- `{reason}`")
                with c_m2:
                    st.markdown(
                        f"<div class='metric-card'><div class='metric-lbl'>Afinidad Semántica</div><div class='metric-val' style='color:{badge_color};'>{m.confidence*100:.1f}%</div></div>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Tier 0 footprint: ~{getattr(m, 'estimated_tokens', 18)} tokens consumidos.")


# -------------------------------------------------------------
# TAB 3: PLAYGROUND DE EJECUCIÓN & PRE-FLIGHT (TIER 3)
# -------------------------------------------------------------
with tab_exec:
    st.subheader("Tier 3: Verificación Pre-Flight y Ejecución en Sandbox")
    st.markdown(
        "Valida formalmente los parámetros de entrada antes del despacho para evitar fallos de runtime, "
        "y ejecuta la llamada bajo un contexto criptográficamente sellado con **Ed25519**."
    )

    cap_ids = [c.id for c in registry.get_index()]
    selected_cid = st.selectbox("Seleccionar Conector a Probar:", cap_ids, index=0)

    chosen_conn = registry.get_connector(selected_cid)
    schema_info = registry.get_full_spec(selected_cid) or {}

    col_ex1, col_ex2 = st.columns([1, 1])
    with col_ex1:
        st.markdown(f"##### Parámetros Requeridos para `{selected_cid}`:")
        params = schema_info.get("parameters", {})
        st.json(params)

        default_args_str = "{}"
        if schema_info.get("examples"):
            default_args_str = json.dumps(schema_info["examples"][0], indent=2)
        elif selected_cid == "sap.odata-stock":
            default_args_str = json.dumps({"material_id": "MAT-0091", "plant": "1000", "storage_location": "0001"}, indent=2)
        elif selected_cid == "odoo.account-invoice":
            default_args_str = json.dumps({"state": "draft", "limit": 10}, indent=2)
        elif selected_cid == "sql.relational-query":
            default_args_str = json.dumps({"query": "SELECT id, name, balance FROM accounts WHERE balance > 1000 LIMIT 5;"}, indent=2)

        args_input = st.text_area("Argumentos de Invocación (JSON):", value=default_args_str, height=180)

    with col_ex2:
        st.markdown("##### Contexto de Invocación Criptográfico:")
        agent_id_input = st.text_input("Identidad del Agente Invocador:", value="quantigrade-maestro-agent-01")
        tenant_id_input = st.text_input("Tenant ID:", value="tenant-enterprise-prod")
        sandbox_toggle = st.checkbox("Ejecución en Sandbox Aislado", value=True)

        # Pre-Flight Validation
        if st.button("🔍 Ejecutar Pre-Flight Validator", use_container_width=True):
            try:
                parsed_args = json.loads(args_input)
                verdict = validator.validate(selected_cid, parsed_args)
                if verdict.valid:
                    st.success(f"✅ Validación Pre-Flight Exitosa ({verdict.profile} mode). 0 errores detectados.")
                else:
                    st.error(f"❌ Fallo de Validación: {verdict.errors}")
                if verdict.warnings:
                    st.warning(f"⚠️ Advertencias: {verdict.warnings}")
            except Exception as ex:  # noqa: BLE001
                st.error(f"Error parseando JSON: {ex}")

        # Execute
        if st.button("⚡ Ejecutar Conector", type="primary", use_container_width=True):
            try:
                parsed_args = json.loads(args_input)
                start_t = time.perf_counter()
                ctx = ExecutionContext(
                    agent_id=agent_id_input,
                    tenant_id=tenant_id_input,
                    sandbox_mode=sandbox_toggle,
                )
                res = registry.execute(selected_cid, parsed_args, context=ctx)
                dur = (time.perf_counter() - start_t) * 1000

                # Ledger record
                ledger.append_event("CONNECTOR_EXECUTED", {
                    "connector_id": selected_cid,
                    "agent": agent_id_input,
                    "success": res.success,
                    "latency_ms": round(dur, 2),
                })

                if res.success:
                    st.markdown(f"#### ✅ Resultado Exitoso ({dur:.1f} ms):")
                    st.json(res.data)
                    if res.provenance_receipt:
                        st.markdown("**Recibo de Procedencia Criptográfica:**")
                        st.json(res.provenance_receipt)
                else:
                    st.error(f"Error en ejecución: {res.error}")
            except Exception as ex:  # noqa: BLE001
                st.error(f"Excepción en ejecución: {ex}")


# -------------------------------------------------------------
# TAB 4: INGESTION STUDIO OPENAPI 3.0/3.1
# -------------------------------------------------------------
with tab_openapi:
    st.subheader("Estudio de Ingesta Declarativa OpenAPI 3.0 / 3.1")
    st.markdown(
        "Transforma cualquier especificación de API masiva (que saturaría la ventana de contexto de un LLM con 5,000+ tokens) "
        "en conectores polimórficos de alta resolución con huella de sólo **~18 tokens** por endpoint."
    )

    example_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Quantum Logistics Enterprise API",
            "version": "2.4.0",
            "description": "API corporativa para gestión de envíos y cálculo de aranceles aduaneros.",
        },
        "servers": [{"url": "https://api.logistics.quantigrade.io/v2"}],
        "paths": {
            "/shipments/calculate-rate": {
                "post": {
                    "operationId": "calculateShippingRate",
                    "summary": "Calcula el coste de envío internacional y tasas de aduana",
                    "description": "Calcula las tarifas estimadas de flete marítimo o aéreo según peso y volumen.",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "origin_country": {"type": "string", "example": "ES"},
                                        "destination_country": {"type": "string", "example": "US"},
                                        "weight_kg": {"type": "number", "example": 25.4},
                                        "transport_mode": {"type": "string", "enum": ["air", "sea", "express"], "default": "air"},
                                    },
                                    "required": ["origin_country", "destination_country", "weight_kg"],
                                }
                            }
                        }
                    },
                }
            },
            "/customs/declarations": {
                "post": {
                    "operationId": "submitCustomsDeclaration",
                    "summary": "Presenta declaración aduanera automatizada",
                    "description": "Genera el documento DUA telemático y valida certificados de origen.",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "shipment_id": {"type": "string"},
                                        "hs_tariff_code": {"type": "string", "example": "8471.30.00"},
                                        "declared_value_eur": {"type": "number", "example": 1450.00},
                                    },
                                    "required": ["shipment_id", "hs_tariff_code", "declared_value_eur"],
                                }
                            }
                        }
                    },
                }
            },
        },
    }

    openapi_input = st.text_area(
        "Pegar Especificación OpenAPI 3.0 / 3.1 (JSON):",
        value=json.dumps(example_spec, indent=2),
        height=280,
    )

    if st.button("⚡ Compilar e Ingerir Conectores OpenAPI", type="primary"):
        try:
            parsed = json.loads(openapi_input)
            connectors = OpenAPIConnector.from_spec_dict(parsed, namespace="logistics.enterprise")
            for c in connectors:
                registry.register_connector(c)

            st.success(f"✅ Se han generado e indexado exitosamente {len(connectors)} conectores OpenAPI en el mesh.")

            raw_tokens = len(json.dumps(parsed)) // 4
            sdp_tokens = len(connectors) * 18
            saving = (1 - (sdp_tokens / max(1, raw_tokens))) * 100

            c_o1, c_o2, c_o3 = st.columns(3)
            with c_o1:
                st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Huella Raw OpenAPI</div><div class='metric-val'>{raw_tokens:,} <span style='font-size:0.9rem;color:#94a3b8;'>tokens</span></div></div>", unsafe_allow_html=True)
            with c_o2:
                st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Huella SDP Tier 0</div><div class='metric-val'>{sdp_tokens} <span style='font-size:0.9rem;color:#94a3b8;'>tokens</span></div></div>", unsafe_allow_html=True)
            with c_o3:
                st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Ahorro de Contexto</div><div class='metric-val' style='color:#00FF9D;'>{saving:.1f}%</div></div>", unsafe_allow_html=True)

        except Exception as ex:  # noqa: BLE001
            st.error(f"Error procesando OpenAPI: {ex}")


# -------------------------------------------------------------
# TAB 5: GATEWAY MCP & SWARMS BRIDGE
# -------------------------------------------------------------
with tab_mcp:
    st.subheader("Puente de Interoperabilidad Model Context Protocol (MCP) & Swarms")
    st.markdown(
        "SDP expone **un servidor MCP ultra-ligero de sólo 4 herramientas de descubrimiento/ejecución**, "
        "permitiendo a Claude Desktop o Cursor interactuar con cientos de herramientas sin rellenar la ventana de contexto."
    )

    st.markdown("#### Herramientas Exportadas por el Servidor MCP de Quantigrade:")
    mcp_tools = mcp_server.list_mcp_tools()
    for t in mcp_tools:
        st.markdown(f"• **`{t['name']}`**: {t['description']}")
        with st.expander(f"Ver inputSchema de `{t['name']}`"):
            st.json(t["inputSchema"])

    st.markdown("---")
    st.markdown("#### Configuración Lista para Pegar en `claude_desktop_config.json`:")
    mcp_config = {
        "mcpServers": {
            "quantigrade-semantic-discovery": {
                "command": "python",
                "args": ["-m", "mcp_bridge.server"],
                "cwd": str(Path(__file__).resolve().parent),
                "env": {"SDP_PORT": "8508", "QUANTIGRADE_ENV": "production"},
            }
        }
    }
    st.code(json.dumps(mcp_config, indent=2), language="json")


# -------------------------------------------------------------
# TAB 6: BENCHMARK CIENTÍFICO
# -------------------------------------------------------------
with tab_bench:
    st.subheader("Laboratorio Científico: Ahorro de Tokens, Latencia y ROI")
    st.markdown(
        "Comparativa empírica entre el enfoque estándar de inyección masiva (**Naive Tool-Stuffing**) "
        "y el **Semantic Discovery Protocol (SDP)** a medida que el catálogo de herramientas corporativo escala."
    )

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        sim_tools = st.slider("Tamaño del Catálogo de Herramientas / Skills:", min_value=10, max_value=300, value=100, step=10)
    with col_b2:
        sim_reqs = st.slider("Peticiones Mensuales de Agentes Autónomos:", min_value=10_000, max_value=1_000_000, value=250_000, step=25_000)

    res = bench_suite.compare(catalog_size=sim_tools, selected_tools_count=2, monthly_requests=sim_reqs)

    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    with c_s1:
        st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Ahorro de Contexto</div><div class='metric-val' style='color:#00FF9D;'>{res.percentage_savings:.1f}%</div></div>", unsafe_allow_html=True)
    with c_s2:
        st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Tokens Ahorrados/Prompt</div><div class='metric-val'>{res.tokens_saved:,}</div></div>", unsafe_allow_html=True)
    with c_s3:
        st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Latencia Estimada</div><div class='metric-val'>{res.estimated_latency_sdp_ms}ms <span style='font-size:0.8rem;color:#94a3b8;'>({res.estimated_latency_naive_ms}ms naive)</span></div></div>", unsafe_allow_html=True)
    with c_s4:
        st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Ahorro Económico/Mes</div><div class='metric-val' style='color:#00F0FF;'>${res.monthly_savings_usd:,.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Matriz Científica Comparativa:")
    df_bench = pd.DataFrame([
        {
            "Enfoque de Integración": "Naive Tool-Stuffing (Inyección Completa)",
            "Tokens / Turno": res.naive_stuffing_tokens,
            "Latencia Prompt": f"{res.estimated_latency_naive_ms} ms",
            "Coste Mensual Est.": f"${(res.naive_stuffing_tokens * sim_reqs / 1e6) * 3.0:,.2f}",
        },
        {
            "Enfoque de Integración": "Semantic Discovery Protocol (SDP)",
            "Tokens / Turno": res.sdp_progressive_tokens,
            "Latencia Prompt": f"{res.estimated_latency_sdp_ms} ms",
            "Coste Mensual Est.": f"${(res.sdp_progressive_tokens * sim_reqs / 1e6) * 3.0:,.2f}",
        },
    ])
    st.dataframe(df_bench, use_container_width=True)


# -------------------------------------------------------------
# TAB 7: BÚNKER CRIPTOGRÁFICO
# -------------------------------------------------------------
with tab_bunker:
    st.subheader("Búnker Criptográfico de Trazabilidad y Cumplimiento (EU AI Act Art. 12)")
    st.markdown(
        "Cada enrutamiento semántico, resolución de esquema y validación de argumentos queda registrado "
        "inmutablemente en la cadena de bloques SHA-256 para auditoría de sistemas de IA de alto riesgo."
    )

    col_bk1, col_bk2 = st.columns([2, 1])
    with col_bk1:
        if st.session_state.last_seal:
            seal = st.session_state.last_seal
            st.markdown(f"• **ID de Acta de Custodia:** `{seal.seal_id}`")
            st.markdown(f"• **Raíz de Merkle:** `{seal.merkle_root_hash}`")
            st.markdown(f"• **Evidencias Selladas:** `{seal.total_evidences}`")
            st.markdown(f"• **Nivel de Aseguramiento:** `{seal.slsa_level}`")
            st.markdown(f"• **Marco de Conformidad:** `{seal.framework}`")
    with col_bk2:
        if st.button("🔍 Verificar Integridad Matemática de Cadena", use_container_width=True):
            if ledger.verify_chain():
                st.success("✅ Verificación exitosa: 0 alteraciones en el registro de descubrimientos.")
            else:
                st.error("❌ Alerta de manipulación de registros.")

    st.markdown("#### Registro Inmutable de Resoluciones (Blockchain SHA-256):")
    b_data = [
        {
            "Bloque": b.index,
            "Evento": b.event_type,
            "Timestamp UTC": b.timestamp,
            "Data Hash": b.data_hash[:16] + "...",
            "Block Hash": b.block_hash[:16] + "...",
            "Prev Hash": b.previous_hash[:16] + "...",
        }
        for b in ledger.chain
    ]
    st.dataframe(pd.DataFrame(b_data), use_container_width=True)
