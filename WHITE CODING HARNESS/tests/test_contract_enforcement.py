"""Tests for Contract Locker and Boundary Enforcement."""

from core.contract_locker import ContractLocker, StepContract
from core.whiteboard_architect import WhiteboardArchitect


def test_lock_specification():
    architect = WhiteboardArchitect()
    spec = architect.create_spec("Microservice for Billing")
    locker = ContractLocker()

    contracts = locker.lock_specification(spec)
    assert len(contracts) == 2
    assert contracts[0].target_file == "models.py"
    assert contracts[1].target_file == "service.py"
    assert len(contracts[0].contract_hash) == 64


def test_boundary_enforcement_clean_code():
    locker = ContractLocker()
    contract = StepContract(
        contract_id="CTR-01",
        step_number=1,
        title="Models",
        target_file="models.py",
        test_file="test_models.py",
        spec_hash="dummy",
        allowed_imports=["json", "pydantic", "typing"],
        forbidden_imports=["subprocess", "pickle"],
        required_classes=["MyModel"],
        required_methods=["to_dict"],
    )

    clean_code = """
import json
from typing import Dict, Any
from pydantic import BaseModel

class MyModel(BaseModel):
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
"""
    valid, violations = locker.validate_code_boundaries(contract, clean_code)
    assert valid is True
    assert len(violations) == 0


def test_boundary_enforcement_forbidden_import():
    locker = ContractLocker()
    contract = StepContract(
        contract_id="CTR-02",
        step_number=2,
        title="Models",
        target_file="models.py",
        test_file="test_models.py",
        spec_hash="dummy",
        allowed_imports=["json"],
        forbidden_imports=["subprocess", "pickle"],
        required_classes=["MyModel"],
        required_methods=["to_dict"],
    )

    breached_code = """
import subprocess
import pickle

class MyModel:
    def to_dict(self):
        return {}
"""
    valid, violations = locker.validate_code_boundaries(contract, breached_code)
    assert valid is False
    assert any("subprocess" in v for v in violations)
    assert any("pickle" in v for v in violations)
