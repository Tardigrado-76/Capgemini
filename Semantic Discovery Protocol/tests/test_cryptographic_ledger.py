"""Tests for Cryptographic Ledger and Merkle Sealer in SDP."""

from provenance.merkle_sealer import DiscoveryMerkleSealer
from provenance.sha256_ledger import DiscoveryLedger


def test_discovery_ledger_tamper_detection():
    ledger = DiscoveryLedger()
    assert len(ledger.chain) == 1

    ledger.append_event("CAPABILITY_ROUTED", {"query": "transcribe audio", "top_k": 2})
    ledger.append_event("SCHEMA_HYDRATED", {"capability_id": "mcp.m3cp-audio-transcribe"})
    assert len(ledger.chain) == 3
    assert ledger.verify_chain() is True

    # Tamper with block payload
    ledger.chain[1].payload["query"] = "TAMPERED"
    assert ledger.verify_chain() is False


def test_discovery_merkle_sealer():
    sealer = DiscoveryMerkleSealer()
    sealer.add_evidence("ROUTING_EVENT", "EV-01", {"top_match": "skill.code-doctor"})
    sealer.add_evidence("VALIDATION_EVENT", "EV-02", {"valid": True})

    root = sealer.compute_root()
    assert len(root) == 64

    seal = sealer.seal()
    assert seal.total_evidences == 2
    assert seal.merkle_root_hash == root
    assert "EU AI Act" in seal.framework
