"""Tests for Multi-Level Capability Argument Validator."""

from protocol.registry import CapabilityRegistry
from protocol.validator import MultiLevelValidator


def test_validator_valid_arguments():
    reg = CapabilityRegistry()
    validator = MultiLevelValidator(reg)

    args = {"path": "src/app.py", "auto_fix": True}
    verdict = validator.validate("skill.code-doctor", args)
    assert verdict.valid is True
    assert len(verdict.errors) == 0


def test_validator_missing_required():
    reg = CapabilityRegistry()
    validator = MultiLevelValidator(reg)

    args = {"auto_fix": True}  # Missing 'path'
    verdict = validator.validate("skill.code-doctor", args)
    assert verdict.valid is False
    assert any("path" in err for err in verdict.errors)


def test_validator_type_mismatch():
    reg = CapabilityRegistry()
    validator = MultiLevelValidator(reg)

    args = {"path": 12345}  # Expected string, got int
    verdict = validator.validate("skill.code-doctor", args)
    assert verdict.valid is False
    assert any("Type mismatch" in err for err in verdict.errors)
