"""Tests for Cryptographic Ledger and Merkle Evidence Bunker."""

from provenance.merkle_sealer import MerkleEvidenceBunker
from provenance.sha256_ledger import CryptographicLedger


def test_cryptographic_ledger_integrity():
    ledger = CryptographicLedger()
    assert len(ledger.chain) == 1  # Genesis block

    b1 = ledger.append_event("WHITEBOARD_LOCKED", {"spec_hash": "a" * 64})
    b2 = ledger.append_event("CONTRACT_LOCKED", {"contract_id": "CTR-01"})
    assert b1.block_hash is not None
    assert b2.block_hash is not None
    assert len(ledger.chain) == 3
    assert ledger.verify_chain() is True


def test_cryptographic_ledger_tamper_detection():
    ledger = CryptographicLedger()
    ledger.append_event("WHITEBOARD_LOCKED", {"spec_hash": "a" * 64})
    ledger.append_event("CONTRACT_LOCKED", {"contract_id": "CTR-01"})
    assert ledger.verify_chain() is True

    # Tamper with block 1 payload
    ledger.chain[1].payload["spec_hash"] = "tampered"
    assert ledger.verify_chain() is False


def test_merkle_evidence_bunker_seal():
    bunker = MerkleEvidenceBunker()
    bunker.add_evidence("WHITEBOARD_SPEC", "SPEC-001", {"name": "microservice"})
    bunker.add_evidence("CONTRACT", "CTR-001", {"file": "models.py"})
    bunker.add_evidence("CODE_DIFF", "CODE-001", "def main(): pass")

    root = bunker.compute_root()
    assert len(root) == 64
    assert root != "0" * 64

    seal = bunker.seal("test-system")
    assert seal.total_evidences == 3
    assert seal.merkle_root_hash == root
    assert "EU AI Act Art. 12" in seal.compliance_frameworks
