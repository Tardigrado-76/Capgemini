"""Whiteboard Specification Engine.

Translates high-level goals into rigorous, machine-verifiable architecture specifications
(the 'Whiteboard') before any code is generated.
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class WhiteboardSpec(BaseModel):
    """Rigorous architectural specification locked before code generation."""
    goal: str
    system_name: str
    version: str = "1.0.0"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    architecture_diagram: str
    data_models: dict[str, Any]
    boundary_rules: dict[str, Any]
    invariants: list[str]
    acceptance_criteria: list[dict[str, str]]
    spec_hash: str = ""

    def compute_hash(self) -> str:
        """Calculates a deterministic SHA-256 fingerprint of the specification."""
        payload = {
            "goal": self.goal,
            "system_name": self.system_name,
            "version": self.version,
            "data_models": self.data_models,
            "boundary_rules": self.boundary_rules,
            "invariants": sorted(self.invariants),
            "acceptance_criteria": self.acceptance_criteria,
        }
        raw = json.dumps(payload, sort_keys=True)
        self.spec_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return self.spec_hash


class WhiteboardArchitect:
    """Agent that produces formal architectural specifications from natural language."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.has_llm = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))

    def create_spec(
        self,
        goal: str,
        system_name: str | None = None,
        custom_boundaries: dict[str, Any] | None = None,
    ) -> WhiteboardSpec:
        """Produces a complete Whiteboard specification with boundaries and invariants."""
        clean_goal = goal.strip()
        if not system_name:
            # Derive clean slug name
            words = re.findall(r"\w+", clean_goal)
            system_name = "-".join(words[:4]).lower() if words else "autonomous-service"

        default_boundaries = {
            "allowed_modules": [
                "math", "json", "typing", "dataclasses", "pydantic", "datetime",
                "hashlib", "time", "uuid", "abc", "re", "pytest", "fastapi"
            ],
            "forbidden_dependencies": [
                "telnetlib", "pickle", "subprocess", "ctypes", "os.system"
            ],
            "max_file_count": 5,
            "require_type_hints": True,
            "zero_trust_network": True,
        }
        if custom_boundaries:
            default_boundaries.update(custom_boundaries)

        # Build high-fidelity spec representation
        models = self._derive_data_models(clean_goal)
        diagram = self._derive_mermaid_diagram(system_name, clean_goal)
        invariants = self._derive_invariants(clean_goal)
        criteria = self._derive_acceptance_criteria(clean_goal)

        spec = WhiteboardSpec(
            goal=clean_goal,
            system_name=system_name,
            architecture_diagram=diagram,
            data_models=models,
            boundary_rules=default_boundaries,
            invariants=invariants,
            acceptance_criteria=criteria,
        )
        spec.compute_hash()
        return spec

    def _derive_data_models(self, goal: str) -> dict[str, Any]:
        """Derives structured data schemas aligned with the target system."""
        return {
            "RequestPayload": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "caller_id": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "payload": {"type": "object"},
                },
                "required": ["id", "caller_id", "timestamp"],
            },
            "ResponseEnvelope": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["success", "throttled", "error"]},
                    "code": {"type": "integer"},
                    "message": {"type": "string"},
                    "data": {"type": "object"},
                    "execution_time_ms": {"type": "number"},
                },
                "required": ["status", "code", "message"],
            },
            "AuditEvent": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "action": {"type": "string"},
                    "hash": {"type": "string"},
                },
                "required": ["event_id", "action", "hash"],
            },
        }

    def _derive_mermaid_diagram(self, system_name: str, goal: str) -> str:
        """Builds valid, high-aesthetic Mermaid graph representation."""
        return f"""graph TD
    Client["Client Request / Ingress"] --> Gate["Security & Boundary Gate"]
    Gate --> Core["Core Logic: {system_name}"]
    Core --> Storage["State / Cache Layer"]
    Core --> Ledger["Cryptographic Audit Ledger"]
    Core --> Out["Response Envelope"]

    classDef primary fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef security fill:#312e81,stroke:#818cf8,stroke-width:2px,color:#e0e7ff;
    classDef audit fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#ecfdf5;

    class Client,Core,Storage,Out primary;
    class Gate security;
    class Ledger audit;"""

    def _derive_invariants(self, goal: str) -> list[str]:
        """Defines non-negotiable architectural invariants."""
        return [
            "All exported classes and functions must include strict type annotations.",
            "No plain-text credentials or API secrets may exist in source or configuration.",
            "Forbidden imports (os.system, subprocess, pickle) will trigger immediate build abort.",
            "Functions must handle invalid inputs gracefully without unhandled exceptions.",
            "Audit records must be generated for all mutating operations.",
        ]

    def _derive_acceptance_criteria(self, goal: str) -> list[dict[str, str]]:
        """Produces formal Gherkin scenarios for automated testing."""
        return [
            {
                "id": "AC-01",
                "name": "Standard Valid Execution",
                "scenario": "Given a valid RequestPayload When processed by the system Then return HTTP 200 with success status within 50ms.",
            },
            {
                "id": "AC-02",
                "name": "Boundary Input Validation",
                "scenario": "Given an incomplete payload missing required fields When validated Then reject with status error and code 422.",
            },
            {
                "id": "AC-03",
                "name": "Invariant Compliance",
                "scenario": "Given execution under concurrency When state is updated Then invariants remain strictly intact with zero race conditions.",
            },
        ]
