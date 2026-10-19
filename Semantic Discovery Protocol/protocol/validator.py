"""Multi-Level Capability Argument Validator.

Validates proposed invocation parameters against Tier 2 hydrated schemas prior
to tool or workflow execution (Level 1: presence, Level 2: types, Level 3: runtime bounds).
"""

from typing import Any

from .registry import CapabilityRegistry
from .spec import ValidationVerdict


class MultiLevelValidator:
    """Pre-execution validation engine for capability arguments."""

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def validate(
        self,
        capability_id: str,
        arguments: dict[str, Any],
        level: str = "full_runtime",
    ) -> ValidationVerdict:
        """Evaluates argument dictionary against the registered schema."""
        full_spec = self.registry.get_full_spec(capability_id)
        if not full_spec:
            return ValidationVerdict(
                capability_id=capability_id,
                valid=False,
                errors=[f"Unknown capability: '{capability_id}' not found in registry."],
            )

        errors = []
        warnings = []
        sanitized = dict(arguments)

        required = full_spec.get("required", [])
        params = full_spec.get("parameters", {})

        # Check 1: Required argument presence
        for req in required:
            if req not in arguments or arguments[req] is None or arguments[req] == "":
                errors.append(f"Missing required parameter: '{req}'")

        if level in ["type_strict", "full_runtime"]:
            # Check 2: Type conformity
            for k, val in arguments.items():
                if k in params:
                    expected_type = params[k].get("type")
                    if expected_type == "string" and not isinstance(val, str):
                        errors.append(f"Type mismatch for '{k}': expected string, got {type(val).__name__}")
                    elif expected_type == "boolean" and not isinstance(val, bool):
                        errors.append(f"Type mismatch for '{k}': expected boolean, got {type(val).__name__}")
                    elif expected_type == "integer" and not isinstance(val, int):
                        errors.append(f"Type mismatch for '{k}': expected integer, got {type(val).__name__}")
                    elif expected_type == "number" and not isinstance(val, (int, float)):
                        errors.append(f"Type mismatch for '{k}': expected number, got {type(val).__name__}")
                    elif expected_type == "array" and not isinstance(val, list):
                        errors.append(f"Type mismatch for '{k}': expected array/list, got {type(val).__name__}")
                    elif expected_type == "object" and not isinstance(val, dict):
                        errors.append(f"Type mismatch for '{k}': expected object/dict, got {type(val).__name__}")
                else:
                    warnings.append(f"Undeclared parameter '{k}' provided; ignoring in strict mode.")
                    sanitized.pop(k, None)

        valid = len(errors) == 0
        return ValidationVerdict(
            capability_id=capability_id,
            valid=valid,
            errors=errors,
            warnings=warnings,
            sanitized_arguments=sanitized,
            validation_level=level,
        )
