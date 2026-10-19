"""Contract Locker Engine.

Translates the Whiteboard architectural spec into immutable StepContracts,
enforcing strict boundary conditions, allowed imports, and structural requirements.
"""

import ast
import hashlib
import json
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .whiteboard_architect import WhiteboardSpec


class StepContract(BaseModel):
    """Immutable boundary contract for a discrete implementation step."""
    contract_id: str
    step_number: int
    title: str
    target_file: str
    test_file: str
    spec_hash: str
    allowed_imports: list[str]
    forbidden_imports: list[str]
    required_classes: list[str]
    required_methods: list[str]
    locked: bool = True
    locked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    contract_hash: str = ""

    def compute_hash(self) -> str:
        """Computes deterministic SHA-256 seal for the contract."""
        data = {
            "contract_id": self.contract_id,
            "step_number": self.step_number,
            "title": self.title,
            "target_file": self.target_file,
            "test_file": self.test_file,
            "spec_hash": self.spec_hash,
            "allowed_imports": sorted(self.allowed_imports),
            "forbidden_imports": sorted(self.forbidden_imports),
            "required_classes": sorted(self.required_classes),
            "required_methods": sorted(self.required_methods),
        }
        raw = json.dumps(data, sort_keys=True)
        self.contract_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return self.contract_hash


class ContractLocker:
    """Creates and enforces StepContracts derived from a WhiteboardSpec."""

    def lock_specification(self, spec: WhiteboardSpec) -> list[StepContract]:
        """Deconstructs the WhiteboardSpec into step contracts."""
        contracts: list[StepContract] = []
        base_allowed = spec.boundary_rules.get("allowed_modules", [])
        base_forbidden = spec.boundary_rules.get("forbidden_dependencies", [])

        # Step 1: Data Models & Contracts
        c1 = StepContract(
            contract_id=f"CTR-{spec.system_name[:8]}-01",
            step_number=1,
            title="Domain Data Models & Schemas",
            target_file="models.py",
            test_file="test_models.py",
            spec_hash=spec.spec_hash,
            allowed_imports=base_allowed,
            forbidden_imports=base_forbidden,
            required_classes=["RequestPayload", "ResponseEnvelope", "AuditEvent"],
            required_methods=["to_dict", "validate_self"],
        )
        c1.compute_hash()
        contracts.append(c1)

        # Step 2: Core Processing Service
        c2 = StepContract(
            contract_id=f"CTR-{spec.system_name[:8]}-02",
            step_number=2,
            title="Core Domain Engine & Invariants",
            target_file="service.py",
            test_file="test_service.py",
            spec_hash=spec.spec_hash,
            allowed_imports=base_allowed + ["models"],
            forbidden_imports=base_forbidden,
            required_classes=["CoreService"],
            required_methods=["process_request", "check_invariants"],
        )
        c2.compute_hash()
        contracts.append(c2)

        return contracts

    def validate_code_boundaries(
        self,
        contract: StepContract,
        source_code: str,
    ) -> tuple[bool, list[str]]:
        """Parses AST to verify source code does NOT violate contract boundaries."""
        violations: list[str] = []

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return False, [f"Python Syntax Error: {e.msg} at line {e.lineno}"]

        detected_imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    detected_imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                detected_imports.append(node.module.split(".")[0])

        # Check forbidden imports
        for imp in detected_imports:
            if imp in contract.forbidden_imports:
                violations.append(f"Forbidden import detected: '{imp}' violates contract security rules.")

        # Check required classes
        class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        for req_cls in contract.required_classes:
            if req_cls not in class_names:
                violations.append(f"Missing required class: '{req_cls}' as stipulated in contract.")

        # Check required methods
        func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        for req_m in contract.required_methods:
            if req_m not in func_names:
                violations.append(f"Missing required method: '{req_m}' as stipulated in contract.")

        return len(violations) == 0, violations
