"""Unit tests for Live Mesh Orchestrator and Interceptor."""

import os

from mesh.live_mesh_orchestrator import LiveMeshOrchestrator
from reporting.compliance_passport import CompliancePassportGenerator


def test_live_mesh_evaluate_event():
    orchestrator = LiveMeshOrchestrator()
    meta = {
        "system_name": "Capgemini-Enterprise-Mesh",
        "architecture_diagram": "graph TD\nA-->B",
        "boundary_rules": {"allowed_modules": ["json"]},
        "tests_passed": 10,
        "tests_failed": 0,
        "sbom_present": True,
        "audit_ledger_active": True,
        "hitl_active": True,
        "merkle_active": True,
        "jwt_auth_enabled": True,
        "tls_enforced": True,
        "contract_enforced": True,
    }
    summary = orchestrator.evaluate_event("CI_CD_BUILD", meta)
    assert summary.system_name == "Capgemini-Enterprise-Mesh"
    assert summary.global_score >= 0.85
    assert summary.all_passed is True
    assert summary.seal is not None
    assert len(summary.seal.merkle_root_hash) == 64
    assert len(orchestrator.ledger.chain) >= 2


def test_passport_generation(tmp_path):
    orchestrator = LiveMeshOrchestrator()
    meta = {
        "system_name": "Test-Banking-Engine",
        "tests_passed": 5,
        "audit_ledger_active": True,
    }
    summary = orchestrator.evaluate_event("TEST_EVENT", meta)
    generator = CompliancePassportGenerator()

    # JSON Export
    json_str = generator.generate_json(summary)
    assert "Test-Banking-Engine" in json_str

    # PDF Export
    pdf_path = os.path.join(tmp_path, "passport.pdf")
    out = generator.generate_pdf(summary, pdf_path)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 500
