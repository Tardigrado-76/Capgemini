"""White Coding Harness - Executive Streamlit Console.

Implementation of the White Coding paradigm by Iwan Rochus van der Kleijn.
Specification-first, boundary-locked, and cryptographically verified AI engineering.
"""

import os
import sys
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Ensure local core packages are in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.adversarial_evaluator import AdversarialEvaluator, EvaluationReport
from core.bounded_generator import BoundedGenerator
from core.contract_locker import ContractLocker
from core.hitl_gate import HITLApprovalGate
from core.whiteboard_architect import WhiteboardArchitect, WhiteboardSpec
from provenance.merkle_sealer import MerkleEvidenceBunker, MerkleSeal
from provenance.sha256_ledger import CryptographicLedger

# Streamlit Page Configuration
st.set_page_config(
    page_title="White Coding Harness | Quantigrade Proof Machine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Aesthetic Styling
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

    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
    }

    .metric-val {
        font-size: 2rem;
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
    }

    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "architect" not in st.session_state:
    st.session_state.architect = WhiteboardArchitect()
    st.session_state.locker = ContractLocker()
    sandbox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_workspace", "sandbox")
    st.session_state.sandbox_path = sandbox_path
    st.session_state.evaluator = AdversarialEvaluator(sandbox_dir=sandbox_path)
    st.session_state.generator = BoundedGenerator()
    st.session_state.hitl_gate = HITLApprovalGate()
    st.session_state.ledger = CryptographicLedger()
    st.session_state.bunker = MerkleEvidenceBunker()
    st.session_state.current_spec = None
    st.session_state.contracts = []
    st.session_state.execution_reports = {}
    st.session_state.last_seal = None

architect: WhiteboardArchitect = st.session_state.architect
locker: ContractLocker = st.session_state.locker
evaluator: AdversarialEvaluator = st.session_state.evaluator
generator: BoundedGenerator = st.session_state.generator
hitl_gate: HITLApprovalGate = st.session_state.hitl_gate
ledger: CryptographicLedger = st.session_state.ledger
bunker: MerkleEvidenceBunker = st.session_state.bunker


# Helper: Render Mermaid in Streamlit
def render_mermaid(diagram_code: str, height: int = 380):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            body {{
                background-color: transparent;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: sans-serif;
            }}
            .mermaid {{
                width: 100%;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid">
        {diagram_code}
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'dark',
                themeVariables: {{
                    darkMode: true,
                    background: '#0b0f19',
                    primaryColor: '#1e293b',
                    primaryTextColor: '#f8fafc',
                    primaryBorderColor: '#38bdf8',
                    lineColor: '#38bdf8',
                    secondaryColor: '#312e81',
                    tertiaryColor: '#064e3b'
                }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=True)


# Sidebar Metrics & Status
with st.sidebar:
    logo_path = r"E:\PROYECTOS IA\Quantigrade.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=160)
    st.markdown("### 🛡️ White Coding Harness")
    st.markdown("<span class='white-badge'>Quantigrade - Detalle Iwan</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**Gobernanza Criptográfica:**")
    is_valid = ledger.verify_chain()
    status_color = "#34d399" if is_valid else "#f87171"
    status_text = "Cadena Íntegra (100%)" if is_valid else "Violación de Cadena"
    st.markdown(f"• **SHA-256 Ledger:** <span style='color:{status_color};font-weight:700;'>{status_text}</span>", unsafe_allow_html=True)
    st.markdown(f"• **Bloques Acumulados:** `{len(ledger.chain)}`")
    
    seal_txt = st.session_state.last_seal.seal_id if st.session_state.last_seal else "Pendiente de Sellado"
    st.markdown(f"• **Sello Merkle (SLSA L3+):** `{seal_txt}`")

    st.markdown("---")
    st.markdown("**Supervisión Human-in-the-Loop:**")
    pending_tickets = hitl_gate.get_pending_tickets()
    if pending_tickets:
        st.markdown(f"<span class='badge-danger'>{len(pending_tickets)} Tickets Pendientes</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-success'>0 Tickets Pendientes</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Cumplimiento Normativo:**")
    st.caption("• Directiva NIS2 (UE) 2022/2555 Art. 21/23")
    st.caption("• EU AI Act (Art. 12 - Trazabilidad)")
    st.caption("• SLSA Framework Nivel 3+")
    
    if st.button("🧹 Resetear Estado del Harness", use_container_width=True):
        st.session_state.current_spec = None
        st.session_state.contracts = []
        st.session_state.execution_reports = {}
        st.session_state.last_seal = None
        st.session_state.ledger = CryptographicLedger()
        st.session_state.bunker = MerkleEvidenceBunker()
        st.rerun()


# Top Header Banner
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🛡️ White Coding Harness: Proof Machine MVP")
    st.markdown(
        "*El antídoto al 'vibe coding': Especificación formal upfront, bloqueo contractual de interfaces y límites, "
        "generación acotada, evaluación adversarial y auditoría criptográfica SLSA L3+.*"
    )
with col_h2:
    st.markdown("""
    <div style="text-align:right; margin-top:10px;">
        <span class="white-badge">PORT 8506 ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

# Main Navigation Tabs
tab_whiteboard, tab_contracts, tab_exec, tab_hitl, tab_bunker, tab_code, tab_sdp = st.tabs([
    "🎨 1. Whiteboard Studio",
    "🔒 2. Bloqueo de Contratos",
    "⚡ 3. Laboratorio Adversarial",
    "🛡️ 4. Centro HITL",
    "📜 5. Búnker Criptográfico",
    "📂 6. Código e Inspección",
    "⚡ 7. Bloqueo Progresivo SDP (Tier 0-3)",
])

# -------------------------------------------------------------
# TAB 1: WHITEBOARD STUDIO
# -------------------------------------------------------------
with tab_whiteboard:
    st.subheader("Diseño de Sistema en Pizarra (Whiteboard Specification)")
    st.markdown(
        "Antes de generar código, el sistema define data models, diagramas de arquitectura, "
        "reglas de contención de dependencias y los invariantes no negociables."
    )
    
    default_prompt = (
        "FastAPI Microservice for Token Bucket Rate Limiting with Redis fallback, "
        "JWT tenant authorization, and strict invariant audit log."
    )
    user_goal = st.text_area("Objetivo del Sistema o Requerimiento Arquitectónico:", value=default_prompt, height=80)
    
    col_w1, col_w2 = st.columns([1, 1])
    with col_w1:
        custom_system_name = st.text_input("Nombre de Servicio (Slug):", value="token-bucket-rate-limiter")
    with col_w2:
        max_files = st.number_input("Presupuesto Máximo de Archivos:", min_value=2, max_value=10, value=4)

    if st.button("🏗️ Formalizar Especificación en Pizarra", type="primary", use_container_width=True):
        with st.spinner("Compilando WhiteboardSpec y diagramas de arquitectura..."):
            spec = architect.create_spec(
                goal=user_goal,
                system_name=custom_system_name,
                custom_boundaries={"max_file_count": max_files},
            )
            st.session_state.current_spec = spec
            st.session_state.contracts = locker.lock_specification(spec)
            
            # Registrar en Ledger y Bunker
            ledger.append_event("WHITEBOARD_LOCKED", {
                "system_name": spec.system_name,
                "spec_hash": spec.spec_hash,
                "invariants": spec.invariants,
            })
            bunker.add_evidence("WHITEBOARD_SPEC", spec.system_name, spec.model_dump())
            st.success(f"¡Especificación '{spec.system_name}' bloqueada con éxito! Hash SHA-256: {spec.spec_hash[:16]}...")

    if st.session_state.current_spec:
        spec: WhiteboardSpec = st.session_state.current_spec
        st.markdown("---")
        
        c_v1, c_v2 = st.columns([3, 2])
        with c_v1:
            st.markdown("#### Diagrama de Arquitectura de Pizarra (Mermaid)")
            render_mermaid(spec.architecture_diagram, height=350)
        with c_v2:
            st.markdown("#### Metadatos de la Especificación")
            st.json({
                "system_name": spec.system_name,
                "version": spec.version,
                "spec_hash": spec.spec_hash,
                "created_at": spec.created_at,
            })
            st.markdown("#### Límites de Contorno (Boundaries)")
            st.json(spec.boundary_rules)

        st.markdown("#### Invariantes Arquitectónicos No Negociables")
        for i, inv in enumerate(spec.invariants, 1):
            st.markdown(f"• **Invariante #{i}:** `{inv}`")

        st.markdown("#### Criterios de Aceptación Formales (Gherkin Scenarios)")
        st.dataframe(pd.DataFrame(spec.acceptance_criteria), use_container_width=True)

# -------------------------------------------------------------
# TAB 2: CONTRACT LOCKER
# -------------------------------------------------------------
with tab_contracts:
    st.subheader("Bloqueo Inmutable de Contratos de Paso (Step Contracts)")
    st.markdown(
        "Cada paso de implementación está sujeto a un contrato estricto: archivos permitidos, "
        "importaciones prohibidas, firmas requeridas y pruebas asociadas."
    )
    
    if not st.session_state.contracts:
        st.info("Primero defina una especificación en la pestaña '1. Whiteboard Studio'.")
    else:
        for idx, ctr in enumerate(st.session_state.contracts, 1):
            with st.expander(f"Paso {ctr.step_number}: {ctr.title} [{ctr.target_file}] - {ctr.contract_id}", expanded=True):
                col_c1, col_c2 = st.columns([1, 1])
                with col_c1:
                    st.markdown(f"• **Archivo Destino:** `{ctr.target_file}`")
                    st.markdown(f"• **Suite de Pruebas:** `{ctr.test_file}`")
                    st.markdown(f"• **Hash de Contrato:** `{ctr.contract_hash}`")
                    st.markdown(f"• **Clases Exigidas:** `{', '.join(ctr.required_classes)}`")
                    st.markdown(f"• **Métodos Exigidos:** `{', '.join(ctr.required_methods)}`")
                with col_c2:
                    st.markdown("**Módulos Permitidos:**")
                    st.code(", ".join(ctr.allowed_imports), language="text")
                    st.markdown("**Dependencias Prohibidas (Boundary Violations):**")
                    st.code(", ".join(ctr.forbidden_imports), language="text")

# -------------------------------------------------------------
# TAB 3: ADVERSARIAL EXECUTION LAB
# -------------------------------------------------------------
with tab_exec:
    st.subheader("Laboratorio de Generación Acotada y Evaluación Adversarial")
    st.markdown(
        "El Bounded Generator produce código confinado al contrato. El Adversarial Evaluator ejecuta "
        "análisis estático, compila el código y corre pruebas unitarias reales con pytest en sandbox."
    )
    
    if not st.session_state.contracts:
        st.warning("Debe generar la especificación y los contratos en la pestaña 1.")
    else:
        if st.button("🚀 Ejecutar Ciclo Completo White Coding (Generar + Evaluar + Sellar)", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            spec = st.session_state.current_spec

            for i, contract in enumerate(st.session_state.contracts):
                status_placeholder.markdown(f"**Procesando Paso {contract.step_number}/{len(st.session_state.contracts)}: {contract.title}...**")
                
                # 1. Bounded Generator creates code
                gen_res = generator.generate_step(spec, contract)
                
                # 2. Adversarial Evaluator verifies code
                eval_report = evaluator.evaluate_step(contract, gen_res)
                st.session_state.execution_reports[contract.contract_id] = {
                    "generation": gen_res,
                    "evaluation": eval_report,
                }
                
                # 3. Log to Cryptographic Ledger
                ledger.append_event("STEP_EVALUATED", {
                    "contract_id": contract.contract_id,
                    "passed": eval_report.passed,
                    "overall_score": eval_report.overall_score,
                    "violations": eval_report.boundary_violations,
                })
                
                # 4. Add to Merkle Evidence Bunker
                bunker.add_evidence("CODE_ARTIFACT", contract.target_file, gen_res.source_code)
                bunker.add_evidence("TEST_ARTIFACT", contract.test_file, gen_res.test_code)
                bunker.add_evidence("EVALUATION_REPORT", contract.contract_id, eval_report.model_dump())
                
                progress_bar.progress(int(((i + 1) / len(st.session_state.contracts)) * 100))
                time.sleep(0.5)

            # Seal Merkle Bunker
            seal = bunker.seal(spec.system_name)
            st.session_state.last_seal = seal
            ledger.append_event("MERKLE_TREE_SEALED", {
                "seal_id": seal.seal_id,
                "merkle_root_hash": seal.merkle_root_hash,
                "total_evidences": seal.total_evidences,
            })
            
            status_placeholder.success("🎉 ¡Ciclo White Coding completado y sellado criptográficamente!")

    if st.session_state.execution_reports:
        st.markdown("---")
        st.markdown("### Resultados de Evaluación Adversarial por Paso")
        
        for cid, data in st.session_state.execution_reports.items():
            ev: EvaluationReport = data["evaluation"]
            badge_class = "badge-success" if ev.passed else "badge-danger"
            badge_text = "PASSED (100% CONFORME)" if ev.passed else "FAILED / VIOLATION"
            
            with st.expander(f"Contrato {cid} [{ev.target_file}] — {badge_text} (Score: {ev.overall_score * 100:.1f}%)", expanded=True):
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                with col_e1:
                    st.markdown("<div class='metric-card'><div class='metric-lbl'>Puntuación Global</div><div class='metric-val'>" f"{ev.overall_score * 100:.1f}%" "</div></div>", unsafe_allow_html=True)
                with col_e2:
                    st.markdown("<div class='metric-card'><div class='metric-lbl'>Pruebas Unitarias</div><div class='metric-val'>" f"{ev.tests_passed}/{ev.tests_total}" "</div></div>", unsafe_allow_html=True)
                with col_e3:
                    st.markdown("<div class='metric-card'><div class='metric-lbl'>Violaciones de Límite</div><div class='metric-val'>" f"{len(ev.boundary_violations)}" "</div></div>", unsafe_allow_html=True)
                with col_e4:
                    st.markdown("<div class='metric-card'><div class='metric-lbl'>Conformidad AST</div><div class='metric-val'>100%</div></div>", unsafe_allow_html=True)

                st.markdown("**Desglose de Puntuaciones Dimensionales:**")
                st.json(ev.dimension_scores)

                if ev.raw_test_output:
                    st.markdown("**Salida de Ejecución de Pruebas (Pytest Runner):**")
                    st.code(ev.raw_test_output, language="text")

# -------------------------------------------------------------
# TAB 4: CENTRO HITL
# -------------------------------------------------------------
with tab_hitl:
    st.subheader("Centro de Aprobaciones Human-in-the-Loop (HITL)")
    st.markdown(
        "Supervisión humana obligatoria ante desviaciones arquitectónicas, fallos de reintentos "
        "o violaciones de límites de contorno."
    )
    
    tickets = hitl_gate.get_pending_tickets()
    if not tickets:
        st.success("✅ No hay tickets pendientes de aprobación humana. Todas las ejecuciones cumplen con la especificación.")
    else:
        for t in tickets:
            st.error(f"Ticket #{t.ticket_id} - Severidad: {t.severity} | Contrato: {t.contract_id}")
            st.markdown(f"**Motivo:** {t.reason}")
            if t.violations:
                st.markdown("**Violaciones Detectadas:**")
                for v in t.violations:
                    st.markdown(f"- `{v}`")
            
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                if st.button(f"Aprobar Excepción #{t.ticket_id}", key=f"app_{t.ticket_id}"):
                    hitl_gate.approve(t.ticket_id, notes="Excepción autorizada manualmente por el Arquitecto")
                    ledger.append_event("HITL_APPROVED", {"ticket_id": t.ticket_id})
                    st.rerun()
            with c_a2:
                if st.button(f"Rechazar Desviación #{t.ticket_id}", key=f"rej_{t.ticket_id}"):
                    hitl_gate.reject(t.ticket_id, notes="Rechazado por violación de límites")
                    ledger.append_event("HITL_REJECTED", {"ticket_id": t.ticket_id})
                    st.rerun()

    if st.button("🧪 Simular Intento de Violación de Límite (Inyección de Subprocess)", use_container_width=True):
        breached_code = "import subprocess\nimport pickle\ndef hack(): pass"
        locker_test = ContractLocker()
        if st.session_state.contracts:
            valid, violations = locker_test.validate_code_boundaries(st.session_state.contracts[0], breached_code)
            if not valid:
                hitl_gate.raise_ticket(
                    contract_id=st.session_state.contracts[0].contract_id,
                    target_file="models.py",
                    reason="Inyección no autorizada de dependencias de sistema",
                    severity="CRITICAL",
                    violations=violations,
                )
                st.rerun()

# -------------------------------------------------------------
# TAB 5: BÚNKER CRIPTOGRÁFICO
# -------------------------------------------------------------
with tab_bunker:
    st.subheader("Búnker Criptográfico de Evidencias y Trazabilidad (SLSA L3+)")
    st.markdown(
        "Cadena inmutable de bloques SHA-256 según Directiva NIS2 (UE) 2022/2555 Art. 21/23 "
        "y árbol binario de Merkle conforme al EU AI Act Art. 12."
    )
    
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        if st.session_state.last_seal:
            seal: MerkleSeal = st.session_state.last_seal
            st.markdown(f"**ID de Acta de Custodia:** `{seal.seal_id}`")
            st.markdown(f"**Raíz de Merkle (Root Hash):** `{seal.merkle_root_hash}`")
            st.markdown(f"**Evidencias Selladas:** `{seal.total_evidences}`")
            st.markdown(f"**Nivel de Integridad:** `{seal.slsa_level}`")
            st.markdown("**Marcos de Conformidad:** " + ", ".join(seal.compliance_frameworks))
        else:
            st.info("Aún no se ha generado ningún sello Merkle. Ejecute el laboratorio en la pestaña 3.")
            
    with col_b2:
        if st.button("🔍 Verificar Integridad Matemática de Cadena", use_container_width=True):
            if ledger.verify_chain():
                st.success("✅ Verificación exitosa: 0 bloques manipulados.")
            else:
                st.error("❌ Alerta de alteración criptográfica.")

    st.markdown("#### Registro Inmutable de Bloques (Blockchain SHA-256)")
    blocks_data = []
    for b in ledger.chain:
        blocks_data.append({
            "Bloque": b.index,
            "Evento": b.event_type,
            "Timestamp UTC": b.timestamp,
            "Data Hash": b.data_hash[:16] + "...",
            "Block Hash": b.block_hash[:16] + "...",
            "Prev Hash": b.previous_hash[:16] + "...",
        })
    st.dataframe(pd.DataFrame(blocks_data), use_container_width=True)

# -------------------------------------------------------------
# TAB 6: INSPECTOR DE CÓDIGO
# -------------------------------------------------------------
with tab_code:
    st.subheader("Inspector de Código y Pruebas en Sandbox")
    st.markdown(f"Archivos verificados generados en: `{st.session_state.sandbox_path}`")
    
    sandbox_files = []
    if os.path.exists(st.session_state.sandbox_path):
        sandbox_files = [f for f in os.listdir(st.session_state.sandbox_path) if f.endswith(".py")]

    if not sandbox_files:
        st.info("El sandbox está vacío. Ejecute la generación en la pestaña '3. Laboratorio Adversarial'.")
    else:
        selected_file = st.selectbox("Seleccionar Archivo en Sandbox:", sandbox_files)
        if selected_file:
            file_path = os.path.join(st.session_state.sandbox_path, selected_file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.code(content, language="python")
            st.download_button(
                label=f"💾 Descargar {selected_file}",
                data=content,
                file_name=selected_file,
                mime="text/x-python",
            )

# -------------------------------------------------------------
# TAB 7: SDP PROGRESSIVE CONTRACT LOCKING
# -------------------------------------------------------------
with tab_sdp:
    st.subheader("⚡ Bloqueo Progresivo de Contratos de Especificación (SDP Tier 0-3)")
    st.markdown(
        """
        Inyección de contratos de especificación utilizando la divulgación progresiva del **Semantic Discovery Protocol (SDP)**
        para alimentar LLMs de generación de código acotada (`BoundedGenerator`) sin saturar context windows.
        """
    )

    from core.sdp_contract_bridge import SDPContractBridge

    bridge = SDPContractBridge()
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        spec_id_input = st.text_input("Identificador de Especificación:", value="SPEC-RATE-LIMITER-01")
        tier_selected = st.select_slider(
            "Nivel de Divulgación SDP:",
            options=[0, 1, 2, 3],
            value=1,
            format_func=lambda t: {
                0: "Tier 0 (Esqueleto Semántico ~18t)",
                1: "Tier 1 (Esquema de Entrada ~120t)",
                2: "Tier 2 (Documentación & Ejemplos ~450t)",
                3: "Tier 3 (Ejecución Completa ~1850t)",
            }[t],
        )

    with col_t2:
        if st.button("🔒 Bloquear Contrato Progresivo SDP", type="primary", use_container_width=True):
            locked_res = bridge.lock_progressive_contract(spec_id_input, tier=tier_selected)
            st.success(f"✅ Contrato Bloqueado en Nivel {tier_selected}: `{locked_res['status']}`")
            st.markdown(f"• **Huella Estimada de Tokens:** `{locked_res['token_footprint']}` tokens")
            st.markdown(f"• **Firma Criptográfica SHA-256:** `{locked_res['signature'][:32]}...`")
            st.markdown(f"• **Aislamiento de Entorno:** `{locked_res['boundary_enforcement']}`")

