"""Tests for Adversarial Evaluator scoring and test running."""

import shutil
import tempfile

from core.adversarial_evaluator import AdversarialEvaluator
from core.bounded_generator import BoundedGenerator
from core.contract_locker import ContractLocker
from core.whiteboard_architect import WhiteboardArchitect


def test_adversarial_evaluator_passes_valid_code():
    temp_sandbox = tempfile.mkdtemp(prefix="test_sandbox_")
    try:
        architect = WhiteboardArchitect()
        spec = architect.create_spec("Invoice Processing Engine")
        locker = ContractLocker()
        contracts = locker.lock_specification(spec)
        generator = BoundedGenerator()
        evaluator = AdversarialEvaluator(sandbox_dir=temp_sandbox)

        # Generate and evaluate models.py
        gen_models = generator.generate_step(spec, contracts[0])
        report_models = evaluator.evaluate_step(contracts[0], gen_models)

        assert report_models.passed is True
        assert report_models.overall_score >= 0.85
        assert len(report_models.boundary_violations) == 0
        assert report_models.tests_passed >= 1

        # Generate and evaluate service.py (depends on models.py already in sandbox)
        gen_service = generator.generate_step(spec, contracts[1])
        report_service = evaluator.evaluate_step(contracts[1], gen_service)

        assert report_service.passed is True
        assert report_service.overall_score >= 0.85
        assert report_service.tests_passed >= 1
    finally:
        shutil.rmtree(temp_sandbox, ignore_errors=True)
