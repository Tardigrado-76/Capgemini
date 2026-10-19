"""Tests for SDP Live Compliance Probe within Compliance-as-Code Live Mesh."""
from __future__ import annotations

import os
import sys

_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from mesh.sdp_live_connector import SDPLiveComplianceProbe


def test_sdp_live_probe_audit() -> None:
    probe = SDPLiveComplianceProbe()
    audit = probe.audit_connector_compliance("SAPODataConnector")
    assert audit["frameworks_checked"] == ["DORA", "NIS2", "ENS", "EU_AI_ACT"]
    assert audit["is_compliant"] is True
    assert "merkle_root" in audit
    assert audit["connector_name"] == "SAPODataConnector"
    assert audit["encryption_in_transit"] == "TLS_1_3"
