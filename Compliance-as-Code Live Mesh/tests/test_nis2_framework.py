"""Unit tests for NIS2 Regulatory Engine."""

from frameworks.nis2_engine import NIS2Engine


def test_nis2_evaluation_compliant():
    engine = NIS2Engine()
    meta = {
        "system_name": "Healthcare-Portal",
        "boundary_rules": {"allowed_modules": ["math"]},
        "hitl_active": True,
        "audit_ledger_active": True,
        "tests_passed": 5,
        "sbom_present": True,
        "merkle_active": True,
    }
    assessment = engine.evaluate(meta)
    assert assessment.compliant is True
    assert assessment.overall_score >= 0.85
    assert len(assessment.controls) == 5


def test_nis2_evaluation_fails_without_sbom_and_audit():
    engine = NIS2Engine()
    meta = {
        "system_name": "Healthcare-Portal",
        "hitl_active": False,
        "audit_ledger_active": False,
        "sbom_present": False,
        "merkle_active": False,
    }
    assessment = engine.evaluate(meta)
    assert assessment.compliant is False
    assert any(c.status == "NON_COMPLIANT" for c in assessment.controls)
