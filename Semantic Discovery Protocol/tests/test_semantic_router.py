"""Tests for Semantic Intent Router Engine."""

from protocol.registry import CapabilityRegistry
from protocol.semantic_router import SemanticRouter
from protocol.spec import CapabilityType, RoutingQuery


def test_semantic_router_audio_intent():
    reg = CapabilityRegistry()
    router = SemanticRouter(reg)

    query = RoutingQuery(query="Quiero transcribir llamadas de audio y voz a texto", top_k=2)
    matches = router.route(query)

    assert len(matches) > 0
    top = matches[0]
    assert top.capability_id == "mcp.m3cp-audio-transcribe"
    assert top.confidence >= 0.40
    assert any("audio" in r.lower() or "voice" in r.lower() or "keyword" in r.lower() for r in top.match_reasons)


def test_semantic_router_code_quality_intent():
    reg = CapabilityRegistry()
    router = SemanticRouter(reg)

    query = RoutingQuery(query="Auditar código y ejecutar linters con ruff y mypy", top_k=2)
    matches = router.route(query)

    assert len(matches) > 0
    top = matches[0]
    assert top.capability_id == "skill.code-doctor"
    assert top.confidence >= 0.50


def test_semantic_router_filtering_by_type():
    reg = CapabilityRegistry()
    router = SemanticRouter(reg)

    query = RoutingQuery(
        query="Auditoría y revisión de software",
        filter_type=CapabilityType.WORKFLOW_TEMPLATE,
        top_k=5,
    )
    matches = router.route(query)
    for m in matches:
        assert m.type == CapabilityType.WORKFLOW_TEMPLATE
