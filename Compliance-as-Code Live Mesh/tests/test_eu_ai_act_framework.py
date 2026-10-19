"""Unit tests for EU AI Act Regulatory Engine."""

from frameworks.eu_ai_act_engine import EUAIActEngine


def test_eu_ai_act_evaluation_compliant():
    engine = EUAIActEngine()
    meta = {
        "boundary_rules": {"allowed_modules": ["math"]},
        "data_models": {"User": {}},
        "audit_ledger_active": True,
        "merkle_active": True,
        "hitl_active": True,
        "tests_passed": 8,
    }
    assessment = engine.evaluate(meta)
    assert assessment.compliant is True
    assert assessment.overall_score >= 0.85
    assert len(assessment.controls) == 5
    assert any(c.control_id == "EUAI-HUM-14" and c.status == "COMPLIANT" for c in assessment.controls)


def test_eu_ai_act_fails_without_human_oversight():
    engine = EUAIActEngine()
    meta = {
        "hitl_active": False,
        "audit_ledger_active": False,
    }
    assessment = engine.evaluate(meta)
    assert assessment.compliant is False
    assert any(c.control_id == "EUAI-HUM-14" and c.status == "NON_COMPLIANT" for c in assessment.controls)
