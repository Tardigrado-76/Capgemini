"""Unit tests for DORA Regulatory Engine."""

from frameworks.dora_engine import DORAEngine


def test_dora_evaluation_compliant():
    engine = DORAEngine()
    meta = {
        "system_name": "Core-Banking-Adapter",
        "architecture_diagram": "graph TD\nA-->B",
        "boundary_rules": {"allowed_modules": ["json"]},
        "tests_passed": 12,
        "tests_failed": 0,
        "sbom_present": True,
        "audit_ledger_active": True,
    }
    assessment = engine.evaluate(meta)
    assert assessment.compliant is True
    assert assessment.overall_score >= 0.85
    assert len(assessment.controls) == 4
    assert all(len(c.evidence_hash) == 64 for c in assessment.controls)


def test_dora_evaluation_non_compliant_on_failed_tests():
    engine = DORAEngine()
    meta = {
        "system_name": "Core-Banking-Adapter",
        "tests_passed": 2,
        "tests_failed": 10,
        "forbidden_dependencies_detected": ["subprocess"],
        "audit_ledger_active": False,
    }
    assessment = engine.evaluate(meta)
    assert assessment.compliant is False
    assert any(c.status == "NON_COMPLIANT" for c in assessment.controls)
