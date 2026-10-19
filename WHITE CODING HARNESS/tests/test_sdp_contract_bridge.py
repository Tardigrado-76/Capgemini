"""Tests for SDP Progressive Contract Bridge in White Coding Harness."""
from __future__ import annotations

import os
import sys

_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from core.sdp_contract_bridge import SDPContractBridge


def test_sdp_contract_progressive_locking() -> None:
    bridge = SDPContractBridge()
    contract = bridge.lock_progressive_contract("SPEC-001", tier=1)
    assert contract["tier"] == 1
    assert contract["token_footprint"] < 200
    assert contract["signature"] is not None
    assert contract["spec_id"] == "SPEC-001"
    assert contract["status"] == "LOCKED"
