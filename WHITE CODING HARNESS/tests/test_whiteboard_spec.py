"""Tests for Whiteboard Architect and Specification generation."""

from core.whiteboard_architect import WhiteboardArchitect


def test_create_whiteboard_spec_defaults():
    architect = WhiteboardArchitect()
    goal = "FastAPI Microservice for Rate Limiting and Token Bucket with Redis fallback"
    spec = architect.create_spec(goal)

    assert spec.system_name == "fastapi-microservice-for-rate"
    assert "graph TD" in spec.architecture_diagram
    assert "RequestPayload" in spec.data_models
    assert len(spec.invariants) >= 3
    assert len(spec.acceptance_criteria) >= 2
    assert len(spec.spec_hash) == 64


def test_spec_hash_determinism():
    architect = WhiteboardArchitect()
    goal = "Deterministic Ledger Engine"
    spec1 = architect.create_spec(goal)
    spec2 = architect.create_spec(goal)

    assert spec1.spec_hash == spec2.spec_hash
