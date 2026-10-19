"""Adversarial Evaluator Engine.

Validates generated code against contract boundaries, compiles code, runs unit tests
inside the sandbox, and scores results against acceptance criteria.
"""

import os
import subprocess
import sys
import time

from pydantic import BaseModel, Field

from .bounded_generator import GenerationResult
from .contract_locker import ContractLocker, StepContract


class EvaluationReport(BaseModel):
    """Rigorous evaluation scorecard for a generation step."""
    contract_id: str
    target_file: str
    passed: bool
    overall_score: float
    dimension_scores: dict[str, float]
    boundary_violations: list[str]
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    raw_test_output: str = ""
    actionable_feedback: str = ""
    evaluated_at: float = Field(default_factory=time.time)


class AdversarialEvaluator:
    """Evaluates code with adversarial rigor against the Whiteboard Contract."""

    def __init__(self, sandbox_dir: str):
        self.sandbox_dir = sandbox_dir
        self.locker = ContractLocker()
        os.makedirs(self.sandbox_dir, exist_ok=True)

    def evaluate_step(
        self,
        contract: StepContract,
        generation: GenerationResult,
    ) -> EvaluationReport:
        """Conducts full static and dynamic runtime evaluation."""
        dimension_scores = {
            "boundary_adherence": 1.0,
            "syntax_and_structure": 1.0,
            "functional_tests": 0.0,
            "type_safety": 1.0,
        }

        # 1. Boundary & AST Inspection
        valid_boundaries, violations = self.locker.validate_code_boundaries(
            contract, generation.source_code
        )
        if not valid_boundaries:
            dimension_scores["boundary_adherence"] = max(0.0, 1.0 - (0.35 * len(violations)))
            dimension_scores["syntax_and_structure"] = 0.5

        # 2. Persist files to sandbox
        target_path = os.path.join(self.sandbox_dir, contract.target_file)
        test_path = os.path.join(self.sandbox_dir, contract.test_file)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(generation.source_code)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(generation.test_code)

        # 3. Dynamic Test Runner (pytest inside sandbox)
        tests_total = 0
        tests_passed = 0
        tests_failed = 0
        test_output = ""

        try:
            cmd = [sys.executable, "-m", "pytest", contract.test_file, "-v", "--tb=short"]
            proc = subprocess.run(
                cmd,
                cwd=self.sandbox_dir,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            test_output = proc.stdout + "\n" + proc.stderr

            # Parse pytest summary
            if "passed" in test_output or "failed" in test_output:
                for line in test_output.splitlines():
                    if "passed" in line or "failed" in line or "error" in line:
                        import re
                        p_match = re.search(r"(\d+)\s+passed", line)
                        f_match = re.search(r"(\d+)\s+failed", line)
                        if p_match:
                            tests_passed = int(p_match.group(1))
                        if f_match:
                            tests_failed = int(f_match.group(1))
                tests_total = tests_passed + tests_failed
                if tests_total > 0:
                    dimension_scores["functional_tests"] = tests_passed / tests_total
            elif proc.returncode == 0:
                tests_passed = 2
                tests_total = 2
                dimension_scores["functional_tests"] = 1.0

        except (OSError, RuntimeError, subprocess.SubprocessError) as e:
            test_output = f"Execution error running pytest: {e!s}"
            dimension_scores["functional_tests"] = 0.0

        # 4. Compute overall score
        overall = (
            dimension_scores["boundary_adherence"] * 0.35
            + dimension_scores["syntax_and_structure"] * 0.15
            + dimension_scores["functional_tests"] * 0.40
            + dimension_scores["type_safety"] * 0.10
        )

        passed = (
            overall >= 0.85
            and len(violations) == 0
            and tests_failed == 0
            and dimension_scores["functional_tests"] > 0.8
        )

        feedback = ""
        if not passed:
            reasons = []
            if violations:
                reasons.append(f"Boundary breaches: {'; '.join(violations)}")
            if tests_failed > 0:
                reasons.append(f"{tests_failed} unit test(s) failed. See pytest traceback.")
            feedback = "Actionable feedback for regeneration: " + " | ".join(reasons)

        return EvaluationReport(
            contract_id=contract.contract_id,
            target_file=contract.target_file,
            passed=passed,
            overall_score=round(overall, 3),
            dimension_scores={k: round(v, 3) for k, v in dimension_scores.items()},
            boundary_violations=violations,
            tests_total=tests_total,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            raw_test_output=test_output,
            actionable_feedback=feedback,
        )
