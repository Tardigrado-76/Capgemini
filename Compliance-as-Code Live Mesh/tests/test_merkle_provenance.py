"""Unit tests for Cryptographic Provenance and Merkle Bunker."""

from provenance.immutable_ledger import RegulatoryLedger
from provenance.merkle_bunker import MerkleAuditBunker


def test_regulatory_ledger_integrity_and_tamper():
    ledger = RegulatoryLedger()
    assert len(ledger.chain) == 1  # Genesis

    ledger.append_event("DEPLOY_EVENT", {"commit": "abc1234", "score": 0.95})
    ledger.append_event("AUDIT_SEAL", {"seal_id": "SEAL-01"})
    assert len(ledger.chain) == 3
    assert ledger.verify_chain() is True

    # Tamper test
    ledger.chain[1].payload["score"] = 0.0
    assert ledger.verify_chain() is False


def test_merkle_bunker_sealing():
    bunker = MerkleAuditBunker()
    bunker.add_evidence("DORA", "DORA-01", {"status": "COMPLIANT"})
    bunker.add_evidence("NIS2", "NIS2-01", {"status": "COMPLIANT"})
    bunker.add_evidence("ENS", "ENS-01", {"status": "COMPLIANT"})
    bunker.add_evidence("EU_AI_ACT", "EUAI-01", {"status": "COMPLIANT"})

    root = bunker.compute_root()
    assert len(root) == 64
    seal = bunker.seal("Banking-Core")
    assert seal.total_evidences == 4
    assert seal.merkle_root_hash == root
    assert "DORA Reglamento (UE) 2022/2554" in seal.regulatory_certifications
