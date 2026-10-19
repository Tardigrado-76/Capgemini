"""Tests for Capability Registry and Tier 0 Indexing."""

from protocol.registry import CapabilityRegistry
from protocol.spec import CapabilityType


def test_registry_initialization_and_counts():
    reg = CapabilityRegistry()
    assert reg.count() >= 6
    index = reg.get_index()
    assert len(index) >= 6

    # Verify presence of the 3 capability types
    types = {c.type for c in index}
    assert CapabilityType.AGENT_SKILL in types
    assert CapabilityType.MCP_TOOL in types
    assert CapabilityType.WORKFLOW_TEMPLATE in types


def test_registry_tier0_token_efficiency():
    reg = CapabilityRegistry()
    index = reg.get_index()
    for item in index:
        # Tier 0 footprint must remain strictly lightweight (~15-25 tokens)
        assert item.estimated_tokens <= 25
        assert len(item.keywords) >= 3
        assert len(item.description) > 10
