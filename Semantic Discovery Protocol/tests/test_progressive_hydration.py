"""Tests for Progressive Schema Hydrator Engine."""

from protocol.progressive_hydrator import ProgressiveHydrator
from protocol.registry import CapabilityRegistry


def test_progressive_hydration_tiers():
    reg = CapabilityRegistry()
    hydrator = ProgressiveHydrator(reg)

    cid = "mcp.postgres-query"

    # Minimal tier
    h_min = hydrator.hydrate(cid, detail_level="minimal")
    assert h_min is not None
    assert h_min.detail_level == "minimal"
    assert h_min.token_cost <= 150
    assert len(h_min.examples) == 0

    # Standard tier
    h_std = hydrator.hydrate(cid, detail_level="standard")
    assert h_std is not None
    assert h_std.detail_level == "standard"
    assert h_std.token_cost > h_min.token_cost
    assert len(h_std.examples) <= 1

    # Full tier
    h_full = hydrator.hydrate(cid, detail_level="full")
    assert h_full is not None
    assert h_full.detail_level == "full"
    assert h_full.token_cost > h_std.token_cost
    assert len(h_full.documentation) > 0


def test_hydration_unknown_capability():
    reg = CapabilityRegistry()
    hydrator = ProgressiveHydrator(reg)
    assert hydrator.hydrate("non.existent.id") is None
