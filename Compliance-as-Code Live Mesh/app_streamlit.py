"""Compliance-as-Code Live Mesh - Executive Streamlit Console.

Continuous Regulatory Governance across DORA, NIS2, ENS RD 311/2022, and EU AI Act.
Tailored for Iwan Rochus van der Kleijn (Director & Lead Architect at Capgemini).
"""

import os
import sys

import pandas as pd
import streamlit as st

# Ensure local packages are on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ground_truth.pdf_ingestion import IngestedRegulatoryDocument, PDFIngestionService
from ground_truth.rag_cag_mag_engine import RegulatoryMemoryTriad
from ground_truth.sample_generator import generate_sample_regulatory_pdf
from mesh.live_mesh_orchestrator import LiveMeshOrchestrator, MeshEvaluationSummary
from reporting.compliance_passport import CompliancePassportGenerator

# Page Setup
st.set_page_config(
    page_title="Compliance-as-Code Live Mesh | Quantigrade",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark Executive Aesthetic CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
    }

    .metric-val {
        font-size: 2.1rem;
        font-weight: 800;
        color: #38bdf8;
    }

    .metric-lbl {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }

    .white-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = LiveMeshOrchestrator()
    st.session_state.passport_gen = CompliancePassportGenerator()
    st.session_state.current_summary = None
    st.session_state.ground_truth_doc = None
    st.session_state.ground_truth_triad = None
    st.session_state.ground_truth_eval = None

orchestrator: LiveMeshOrchestrator = st.session_state.orchestrator
passport_gen: CompliancePassportGenerator = st.session_state.passport_gen

# Auto-evaluate initial state if empty
if st.session_state.current_summary is None:
    initial_meta = {
        "system_name": "Capgemini-Banking-Microservice-v2",
        "architecture_diagram": "graph TD\nClient-->API\nAPI-->Ledger",
        "boundary_rules": {"allowed_modules": ["math", "json", "typing"]},
        "tests_passed": 14,
        "tests_failed": 0,
        "sbom_present": True,
        "audit_ledger_active": True,
        "hitl_active": True,
        "merkle_active": True,
        "jwt_auth_enabled": True,
        "tls_enforced": True,
        "contract_enforced": True,
    }
    st.session_state.current_summary = orchestrator.evaluate_event("INITIAL_BOOT", initial_meta)

summary: MeshEvaluationSummary = st.session_state.current_summary


# Sidebar: Live Telemetry & Quick Event Ingestion
with st.sidebar:
    logo_path = r"E:\PROYECTOS IA\Quantigrade.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=160)
    st.markdown("### ⚖️ Live Mesh Governance")
    st.markdown("<span class='white-badge'>Quantigrade - Detalle Iwan</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**Estado del Búnker Criptográfico:**")
    is_valid = orchestrator.ledger.verify_chain()
    status_color = "#34d399" if is_valid else "#f87171"
    status_text = "Cadena 100% Íntegra" if is_valid else "Alerta de Alteración"
    st.markdown(f"• **SHA-256 Ledger:** <span style='color:{status_color};font-weight:700;'>{status_text}</span>", unsafe_allow_html=True)
    st.markdown(f"• **Bloques Inmutables:** `{len(orchestrator.ledger.chain)}`")
    if summary.seal:
        st.markdown(f"• **Acta Merkle:** `{summary.seal.seal_id}`")
        st.caption(f"Root: `{summary.seal.merkle_root_hash[:20]}...`")

    st.markdown("---")
    st.markdown("**Supervisión Human-in-the-Loop:**")
    active_incidents = orchestrator.shield.get_blocked_incidents()
    if active_incidents:
        st.markdown(f"<span class='badge-danger'>{len(active_incidents)} Incidentes Bloqueantes</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-success'>0 Incidentes Bloqueantes</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Simulación de Ingress en Vivo:")

    if st.button("🚀 Inyectar Despliegue CI/CD Limpio", use_container_width=True):
        deploy_meta = {
            "system_name": "Quantigrade-Enterprise-Mesh",
            "architecture_diagram": "graph TD\nIngress-->Core-->Ledger",
            "boundary_rules": {"allowed_modules": ["math", "json"]},
            "tests_passed": 24,
            "tests_failed": 0,
            "sbom_present": True,
            "audit_ledger_active": True,
            "hitl_active": True,
            "merkle_active": True,
            "jwt_auth_enabled": True,
            "tls_enforced": True,
            "contract_enforced": True,
        }
        st.session_state.current_summary = orchestrator.evaluate_event("CI_CD_DEPLOY_OK", deploy_meta)
        st.rerun()

    if st.button("⚠️ Simular Incumplimiento (Sin Logging EU AI)", use_container_width=True):
        breached_meta = {
            "system_name": "Capgemini-Unshielded-Agent",
            "audit_ledger_active": False,
            "merkle_active": False,
            "hitl_active": False,
            "tests_passed": 2,
            "tests_failed": 5,
            "sbom_present": False,
        }
        st.session_state.current_summary = orchestrator.evaluate_event("BREACH_SIMULATION", breached_meta)
        st.rerun()


# Top Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("⚖️ Compliance-as-Code Live Mesh")
    st.markdown(
        "*Auditoría regulatoria continua en tiempo de ejecución: DORA (UE 2022/2554), NIS2 (UE 2022/2555), "
        "ENS (RD 311/2022) y EU AI Act (UE 2024/1689). Evidencias selladas con Merkle SLSA L3+.*"
    )
with col_h2:
    st.markdown("""
    <div style="text-align:right; margin-top:10px;">
        <span class="white-badge">PORT 8507 ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

# Main Navigation Tabs
tab_radar, tab_matrix, tab_hitl, tab_sbom, tab_bunker, tab_passport, tab_ground_truth, tab_sdp = st.tabs([
    "🌐 1. Live Mesh Radar",
    "⚖️ 2. Matriz de Controles",
    "🛡️ 3. Breach Shield & HITL",
    "📦 4. CRA SBOM & Paquetes",
    "📜 5. Búnker Criptográfico",
    "📄 6. Pasaporte de Cumplimiento",
    "📚 7. Fuente de Verdad (PDF RAG/CAG/MAG)",
    "⚡ 8. Sonda Live Mesh SDP",
])

# -------------------------------------------------------------
# TAB 1: LIVE MESH RADAR
# -------------------------------------------------------------
with tab_radar:
    st.subheader(f"Radar de Cumplimiento Continuo: {summary.system_name}")
    st.caption(f"Última evaluación sincronizada UTC: {summary.assessed_at}")

    # Top Metric Scorecard
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            f"<div class='metric-card'><div class='metric-lbl'>Global Compliance</div><div class='metric-val'>{summary.global_score*100:.1f}%</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        dora_score = summary.framework_scores.get("DORA", 0)
        st.markdown(
            f"<div class='metric-card'><div class='metric-lbl'>DORA (TIC Risk)</div><div class='metric-val'>{dora_score*100:.1f}%</div></div>",
            unsafe_allow_html=True,
        )
    with c3:
        nis2_score = summary.framework_scores.get("NIS2", 0)
        st.markdown(
            f"<div class='metric-card'><div class='metric-lbl'>NIS2 (Ciberhigiene)</div><div class='metric-val'>{nis2_score*100:.1f}%</div></div>",
            unsafe_allow_html=True,
        )
    with c4:
        ens_score = summary.framework_scores.get("ENS (RD 311/2022)", 0)
        st.markdown(
            f"<div class='metric-card'><div class='metric-lbl'>ENS (Cat. Alta)</div><div class='metric-val'>{ens_score*100:.1f}%</div></div>",
            unsafe_allow_html=True,
        )
    with c5:
        ai_score = summary.framework_scores.get("EU AI Act", 0)
        st.markdown(
            f"<div class='metric-card'><div class='metric-lbl'>EU AI Act (Art. 12)</div><div class='metric-val'>{ai_score*100:.1f}%</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Estado de Conformidad por Marco Normativo")
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        st.markdown("#### 🏦 DORA (Reglamento UE 2022/2554)")
        dora_status = "<span class='badge-success'>CONFORME</span>" if summary.dora.compliant else "<span class='badge-danger'>EN RIESGO</span>"
        st.markdown(f"• **Estado:** {dora_status} | Puntuación: `{summary.dora.overall_score * 100:.1f}%`", unsafe_allow_html=True)
        st.caption("Resiliencia operativa digital, gestión de riesgos TIC de terceros y notificación rápida.")

        st.markdown("#### 🇪🇸 ENS (Real Decreto 311/2022)")
        ens_status = "<span class='badge-success'>CONFORME</span>" if summary.ens.compliant else "<span class='badge-danger'>EN RIESGO</span>"
        st.markdown(f"• **Estado:** {ens_status} | Puntuación: `{summary.ens.overall_score * 100:.1f}%`", unsafe_allow_html=True)
        st.caption("Esquema Nacional de Seguridad: Controles de Acceso, Registro de Auditoría y Protección Cifrada.")

    with col_f2:
        st.markdown("#### 🛡️ NIS2 (Directiva UE 2022/2555)")
        nis2_status = "<span class='badge-success'>CONFORME</span>" if summary.nis2.compliant else "<span class='badge-danger'>EN RIESGO</span>"
        st.markdown(f"• **Estado:** {nis2_status} | Puntuación: `{summary.nis2.overall_score * 100:.1f}%`", unsafe_allow_html=True)
        st.caption("Ciberhigiene obligatoria (Art. 21) y capacidad de alerta temprana en < 24h (Art. 23).")

        st.markdown("#### 🤖 EU AI Act (Reglamento UE 2024/1689)")
        ai_status = "<span class='badge-success'>CONFORME</span>" if summary.eu_ai_act.compliant else "<span class='badge-danger'>EN RIESGO</span>"
        st.markdown(f"• **Estado:** {ai_status} | Puntuación: `{summary.eu_ai_act.overall_score * 100:.1f}%`", unsafe_allow_html=True)
        st.caption("Gestión de Riesgos (Art. 9), Trazabilidad inmutable (Art. 12) y Supervisión Humana (Art. 14).")

# -------------------------------------------------------------
# TAB 2: MATRIZ DE CONTROLES
# -------------------------------------------------------------
with tab_matrix:
    st.subheader("Matriz Dinámica de Controles Evaluados as-Code")
    fw_choice = st.selectbox("Seleccionar Marco Normativo:", ["DORA", "NIS2", "ENS (RD 311/2022)", "EU AI Act"])

    if fw_choice == "DORA":
        controls_data = [c.model_dump() for c in summary.dora.controls]
    elif fw_choice == "NIS2":
        controls_data = [c.model_dump() for c in summary.nis2.controls]
    elif fw_choice == "ENS (RD 311/2022)":
        controls_data = [c.model_dump() for c in summary.ens.controls]
    else:
        controls_data = [c.model_dump() for c in summary.eu_ai_act.controls]

    df_controls = pd.DataFrame(controls_data)
    if "evidence_hash" in df_controls.columns:
        df_controls["evidence_hash"] = df_controls["evidence_hash"].apply(lambda h: f"{h[:16]}...")
    st.dataframe(df_controls, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: BREACH SHIELD & HITL
# -------------------------------------------------------------
with tab_hitl:
    st.subheader("Regulatory Breach Shield & Centro HITL")
    st.markdown(
        "Mecanismo de corte operativo y Human-in-the-Loop obligatorio según **Art. 14 del EU AI Act** "
        "y **Art. 21 de NIS2** para autorizar o mitigar desviaciones."
    )

    incidents = orchestrator.shield.incidents.values()
    if not incidents:
        st.success("✅ Cero incidentes regulatorios. El sistema opera dentro de los límites de contorno permitidos.")
    else:
        for inc in incidents:
            color = "#f87171" if inc.status == "BLOCKED" else "#34d399"
            with st.expander(f"Incidente #{inc.incident_id} [{inc.framework}] - Estado: {inc.status}", expanded=(inc.status == "BLOCKED")):
                st.markdown(f"**Descripción:** {inc.description}")
                st.markdown(f"**Severidad:** `{inc.severity}` | **Creado:** `{inc.created_at}`")
                if inc.violations:
                    st.markdown("**Violaciones Registradas:**")
                    for v in inc.violations:
                        st.markdown(f"- `{v}`")

                if inc.status == "BLOCKED":
                    c_act1, c_act2 = st.columns(2)
                    with c_act1:
                        arch_sig = st.text_input("Firma Digital del Arquitecto:", value="Iwan van der Kleijn (Lead Architect)", key=f"sig_{inc.incident_id}")
                        override_notes = st.text_area("Justificación Técnica de la Excepción:", value="Excepción temporal autorizada bajo supervisión y sandbox mitigado.", key=f"notes_{inc.incident_id}")
                        if st.button(f"Firmar y Autorizar Override #{inc.incident_id}"):
                            orchestrator.shield.authorize_override(inc.incident_id, arch_sig, override_notes)
                            orchestrator.ledger.append_event("REGULATORY_OVERRIDE_APPROVED", {
                                "incident_id": inc.incident_id,
                                "architect_signature": arch_sig,
                            })
                            st.rerun()
                    with c_act2:
                        remed_notes = st.text_input("Notas de Remediación Aplicada:", value="Parche de código aplicado y dependencias corregidas.", key=f"rem_{inc.incident_id}")
                        if st.button(f"Marcar como Remediado #{inc.incident_id}"):
                            orchestrator.shield.remediate_incident(inc.incident_id, remed_notes)
                            orchestrator.ledger.append_event("REGULATORY_INCIDENT_REMEDIATED", {"incident_id": inc.incident_id})
                            st.rerun()
                else:
                    st.info(f"Decisión: {inc.status} | Resuelto por: {inc.architect_signature} | Notas: {inc.decision_notes}")

# -------------------------------------------------------------
# TAB 4: CRA SBOM & DEPENDENCIAS
# -------------------------------------------------------------
with tab_sbom:
    st.subheader("Cyber Resilience Act (CRA) - CycloneDX v1.5 SBOM")
    st.markdown(
        f"**Serial BOM:** `{summary.sbom.serial_number}` | "
        f"**Componentes Auditados:** `{summary.sbom.total_components}` | "
        f"**Vulnerabilidades:** `{summary.sbom.vulnerable_components}`"
    )

    sbom_df = pd.DataFrame([c.model_dump() for c in summary.sbom.components])
    if "sha256_hash" in sbom_df.columns:
        sbom_df["sha256_hash"] = sbom_df["sha256_hash"].apply(lambda h: f"{h[:16]}...")
    st.dataframe(sbom_df, use_container_width=True)

# -------------------------------------------------------------
# TAB 5: BÚNKER CRIPTOGRÁFICO
# -------------------------------------------------------------
with tab_bunker:
    st.subheader("Búnker Criptográfico de Evidencias (SLSA L3+)")
    col_bk1, col_bk2 = st.columns([2, 1])

    with col_bk1:
        if summary.seal:
            st.markdown(f"**ID de Acta Judicial:** `{summary.seal.seal_id}`")
            st.markdown(f"**Raíz de Merkle (Root Hash):** `{summary.seal.merkle_root_hash}`")
            st.markdown(f"**Total de Evidencias Selladas:** `{summary.seal.total_evidences}`")
            st.markdown(f"**Nivel de Seguridad:** `{summary.seal.slsa_level}`")
            st.markdown("**Marcos Certificados:** " + ", ".join(summary.seal.regulatory_certifications))

    with col_bk2:
        if st.button("🔍 Verificar Integridad Matemática de Cadena", use_container_width=True):
            if orchestrator.ledger.verify_chain():
                st.success("✅ Verificación exitosa: Cadena 100% íntegra (0 alteraciones).")
            else:
                st.error("❌ Alerta: Se detectó manipulación no autorizada en el ledger.")

    st.markdown("#### Blockchain de Auditoría Regulatoria (SHA-256 Chained Blocks)")
    blocks_data = [
        {
            "Bloque": b.index,
            "Evento": b.event_type,
            "Timestamp UTC": b.timestamp,
            "Data Hash": b.data_hash[:16] + "...",
            "Block Hash": b.block_hash[:16] + "...",
            "Prev Hash": b.previous_hash[:16] + "...",
        }
        for b in orchestrator.ledger.chain
    ]
    st.dataframe(pd.DataFrame(blocks_data), use_container_width=True)

# -------------------------------------------------------------
# TAB 6: PASAPORTE DE CUMPLIMIENTO
# -------------------------------------------------------------
with tab_passport:
    st.subheader("Generación de Pasaporte Regulatorio Oficial y Dossier Pericial")
    st.markdown(
        "Emisión de informe oficial de peritaje judicial y auditoría regulatoria para presentar ante el "
        "**Banco de España / BCE (DORA)**, **CCN-CERT (ENS)** o la **AESIA (EU AI Act)**."
    )

    pdf_target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pasaporte_Cumplimiento_Regulatorio.pdf")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("#### Certificado Pericial en PDF")
        if st.button("📄 Compilar Pasaporte Oficial en PDF", type="primary", use_container_width=True):
            with st.spinner("Compilando dossier formal con ReportLab y sellado Merkle..."):
                passport_gen.generate_pdf(summary, pdf_target_path)
                st.success(f"¡Pasaporte generado con éxito en: `{pdf_target_path}`!")

        if os.path.exists(pdf_target_path):
            with open(pdf_target_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="⬇️ Descargar Pasaporte PDF Oficial",
                data=pdf_bytes,
                file_name="Pasaporte_Cumplimiento_Regulatorio.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with col_p2:
        st.markdown("#### Exportación de Evidencias en JSON Firmado")
        json_content = passport_gen.generate_json(summary)
        st.download_button(
            label="⬇️ Descargar Dossier JSON Firmado",
            data=json_content,
            file_name="compliance_passport.json",
            mime="application/json",
            use_container_width=True,
        )
        with st.expander("Inspeccionar JSON de Evidencias Criptográficas"):
            st.code(json_content[:1500] + "\n...", language="json")


# -------------------------------------------------------------
# TAB 7: FUENTE DE VERDAD (PDF RAG/CAG/MAG TRIAD)
# -------------------------------------------------------------
with tab_ground_truth:
    st.subheader("📚 Ingesta de Normativa Oficial en PDF como 'Fuente de Verdad'")
    st.markdown(
        "Cargue cualquier documento regulatorio en PDF (**DORA UE 2022/2554**, **NIS2 UE 2022/2555**, "
        "**ENS RD 311/2022** o políticas internas de seguridad). La triada revolucionaria **RAG + CAG + MAG** "
        "convierte el texto en la **autoridad fáctica absoluta**, permitiendo auditar activos de software "
        "con **citaciones periciales exactas de Artículo y Página**."
    )

    col_up1, col_up2 = st.columns([2, 1])

    with col_up1:
        uploaded_pdf = st.file_uploader(
            "📥 Cargar Documento Normativo Oficial (PDF):",
            type=["pdf"],
            help="Suba el texto oficial de la directiva o normativa en PDF.",
        )

    with col_up2:
        st.markdown("**O use una muestra precargada:**")
        if st.button("⚡ Cargar Normativa DORA / NIS2 Oficial de Prueba", use_container_width=True):
            sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Normativa_DORA_NIS2_Referencia_Oficial.pdf")
            generate_sample_regulatory_pdf(sample_path)
            with open(sample_path, "rb") as f:
                pdf_bytes = f.read()
            doc = PDFIngestionService.ingest_pdf(pdf_bytes, filename="Normativa_DORA_NIS2_Referencia_Oficial.pdf")
            st.session_state.ground_truth_doc = doc
            st.session_state.ground_truth_triad = orchestrator.set_ground_truth_document(doc)
            st.session_state.ground_truth_eval = None
            st.success("¡Normativa oficial DORA/NIS2 indexada en la memoria RAG/CAG/MAG!")
            st.rerun()

    if uploaded_pdf is not None and (
        st.session_state.ground_truth_doc is None
        or st.session_state.ground_truth_doc.filename != uploaded_pdf.name
    ):
            with st.spinner("Procesando PDF, extrayendo artículos e indexando grafo MAG..."):
                pdf_bytes = uploaded_pdf.read()
                doc = PDFIngestionService.ingest_pdf(pdf_bytes, filename=uploaded_pdf.name)
                st.session_state.ground_truth_doc = doc
                st.session_state.ground_truth_triad = orchestrator.set_ground_truth_document(doc)
                st.session_state.ground_truth_eval = None
                st.success(f"¡Documento '{uploaded_pdf.name}' procesado y fijado como Fuente de Verdad!")
                st.rerun()

    gt_doc: IngestedRegulatoryDocument = st.session_state.ground_truth_doc
    gt_triad: RegulatoryMemoryTriad = st.session_state.ground_truth_triad

    if gt_doc is not None and gt_triad is not None:
        st.markdown("---")
        # Metadata Card
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1:
            st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Documento Activo</div><div style='font-size:1.1rem;font-weight:700;color:#38bdf8;'>{gt_doc.filename}</div></div>", unsafe_allow_html=True)
        with c_m2:
            st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Páginas Analizadas</div><div class='metric-val'>{gt_doc.total_pages}</div></div>", unsafe_allow_html=True)
        with c_m3:
            st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Artículos Estructurados</div><div class='metric-val'>{gt_doc.total_articles}</div></div>", unsafe_allow_html=True)
        with c_m4:
            st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Mandatos Imperativos</div><div class='metric-val'>{gt_doc.total_mandates}</div></div>", unsafe_allow_html=True)

        st.caption(f"🔒 **Huella Criptográfica SHA-256 (Fuente de Verdad Inmutable):** `{gt_doc.sha256_hash}`")

        # Triad Sub-Tabs
        sub_cag, sub_rag, sub_mag = st.tabs([
            "🧠 1. CAG (Memoria Pinned O(1))",
            "🔍 2. RAG (Búsqueda Híbrida)",
            "🕸️ 3. MAG (Grafo Regulatorio)",
        ])

        with sub_cag:
            st.markdown("#### Artículos Fijados en Caché de Alta Velocidad (CAG)")
            st.caption("Visualización instantánea sin latencia ni pérdida de contexto.")
            art_ids = list(gt_doc.articles.keys())
            selected_art_id = st.selectbox("Seleccione Artículo o Sección:", options=art_ids)
            if selected_art_id:
                art = gt_doc.articles[selected_art_id]
                st.markdown(f"**Título:** `{art.title}` | **Página:** `{art.page_number}`")
                st.text_area("Texto Íntegro del Artículo:", value=art.full_text, height=140)
                if art.mandates:
                    st.markdown("**Mandatos Imperativos Extraídos:**")
                    for m in art.mandates:
                        st.markdown(f"• `{m}`")

        with sub_rag:
            st.markdown("#### Buscador Semántico & de Requerimientos (RAG)")
            query_input = st.text_input("Ingrese consulta regulatoria:", value="plazo máximo de 24 horas notificación incidente")
            if query_input:
                hits = gt_triad.rag.search(query_input, top_k=4)
                if hits:
                    for h in hits:
                        with st.expander(f"[{h.article_id}] Pág. {h.page_number} — Relevancia: {h.relevance_score}", expanded=True):
                            st.markdown(f"**Título:** {h.article_title}")
                            st.markdown(f"**Fragmento Relevante:** *\"{h.snippet}\"*")
                            st.caption(f"Términos coincidentes: {', '.join(h.matched_terms)}")
                else:
                    st.info("No se encontraron coincidencias para la consulta.")

        with sub_mag:
            st.markdown("#### Grafo de Conocimiento Regulatorio (MAG)")
            st.caption("Mapeo topológico entre Normas, Artículos, Mandatos y Variables de Control del Sistema.")
            mag_summary = gt_triad.mag.get_summary()
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                st.metric("Total Nodos en Grafo", mag_summary["total_nodes"])
            with col_g2:
                st.metric("Total Aristas / Relaciones", mag_summary["total_edges"])
            with col_g3:
                st.metric("Controles de Sistema Vinculados", mag_summary["controls_mapped"])

            elements = gt_triad.mag.get_serializable_elements()
            df_edges = pd.DataFrame(elements["edges"])
            if not df_edges.empty:
                st.dataframe(df_edges, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("⚖️ Auditoría Certificada contra la Fuente de Verdad")
        st.markdown("Evalúa la configuración técnica actual frente a los requerimientos del documento cargado.")

        if st.button("🚀 Ejecutar Auditoría contra Fuente de Verdad Activa", type="primary", use_container_width=True):
            system_meta = {
                "system_name": summary.system_name,
                "disaster_recovery_rto_hours": 1.5,
                "incident_reporting_sla_hours": 12.0,
                "encryption_at_rest": True,
                "third_party_risk_assessed": True,
                "human_oversight_active": True,
                "multiregion_failover_tested": True,
            }
            eval_result = orchestrator.evaluate_ground_truth(system_meta)
            st.session_state.ground_truth_eval = eval_result

        gt_eval = st.session_state.ground_truth_eval
        if gt_eval is not None:
            col_sc, col_st = st.columns([1, 2])
            with col_sc:
                st.metric("Puntuación Fuente de Verdad", f"{gt_eval.ground_truth_score}%")
            with col_st:
                status_badge = "<span class='badge-success'>100% CONFORME CON FUENTE DE VERDAD</span>" if gt_eval.is_compliant else "<span class='badge-danger'>INCUMPLIMIENTOS DETECTADOS</span>"
                st.markdown(f"**Dictamen Pericial:** {status_badge}", unsafe_allow_html=True)
                st.caption(f"Controles conformes: {gt_eval.compliant_controls_count} | Brechas: {gt_eval.breached_controls_count}")

            st.markdown("#### Evidencias Periciales con Citación Exacta:")
            for v in gt_eval.verdicts:
                badge = "🟢 CONFORME" if v.compliant else "🔴 INCUMPLIMIENTO"
                with st.expander(f"{badge} — {v.control_field} [{v.normative_article}, Pág. {v.page_number}]", expanded=(not v.compliant)):
                    st.markdown(f"• **Mandato Normativo:** {v.mandate_text}")
                    st.markdown(f"• **Valor Evaluado del Sistema:** `{v.system_value}`")
                    st.markdown(f"• **Dictamen:** {v.explanation}")
                    st.info(f"📜 **Citación Pericial:** `{v.citation}`")
    else:
        st.info("ℹ️ Cargue un archivo PDF arriba o haga clic en '⚡ Cargar Normativa DORA / NIS2 Oficial de Prueba' para activar la Fuente de Verdad.")

# -------------------------------------------------------------
# TAB 8: SDP LIVE MESH PROBE
# -------------------------------------------------------------
with tab_sdp:
    st.subheader("⚡ Sonda de Cumplimiento Continuo para Conectores SDP")
    st.markdown(
        """
        Auditoría automatizada de los conectores dinámicos del **Semantic Discovery Protocol (SDP)**
        (SAP OData, Odoo ERP, SQL, Webhooks) frente a las normativas **DORA, NIS2, ENS RD 311/2022 y EU AI Act**.
        """
    )

    from mesh.sdp_live_connector import SDPLiveComplianceProbe

    probe = SDPLiveComplianceProbe()
    selected_conn = st.selectbox(
        "Seleccione el Conector SDP a auditar:",
        options=["SAPODataConnector", "OdooERPConnector", "SQLDatabaseConnector", "N8NWebhookConnector", "MCPBridgeGateway"],
    )

    if st.button(f"🔍 Auditar Cumplimiento de {selected_conn}", type="primary"):
        audit_res = probe.audit_connector_compliance(selected_conn)
        st.success(f"✅ Conector Certificado: `{audit_res['verdict']}`")

        c_a1, c_a2 = st.columns(2)
        with c_a1:
            st.markdown(f"• **Cifrado en Tránsito:** `{audit_res['encryption_in_transit']}`")
            st.markdown(f"• **Marcos Evaluados:** `{', '.join(audit_res['frameworks_checked'])}`")
            st.markdown(f"• **Raíz Merkle de Evidencia:** `{audit_res['merkle_root'][:32]}...`")
        with c_a2:
            st.json(audit_res["checks"])


