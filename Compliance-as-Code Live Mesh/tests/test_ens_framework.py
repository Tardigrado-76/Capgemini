"""Unit tests for ENS (RD 311/2022) Engine."""

from frameworks.ens_engine import ENSEngine


def test_ens_evaluation_alta_compliant():
    engine = ENSEngine()
    meta = {
        "jwt_auth_enabled": True,
        "audit_ledger_active": True,
        "tls_enforced": True,
        "contract_enforced": True,
        "hitl_active": True,
    }
    assessment = engine.evaluate(meta, target_category="ALTA")
    assert assessment.compliant is True
    assert assessment.overall_score >= 0.90
    assert len(assessment.controls) == 5
    assert all(c.status == "COMPLIANT" for c in assessment.controls)


def test_ens_evaluation_alta_fails_without_audit():
    engine = ENSEngine()
    meta = {
        "jwt_auth_enabled": True,
        "audit_ledger_active": False,
        "tls_enforced": True,
    }
    assessment = engine.evaluate(meta, target_category="ALTA")
    assert assessment.compliant is False
    assert any(c.control_id == "[op.exp.8]" and c.status == "NON_COMPLIANT" for c in assessment.controls)
