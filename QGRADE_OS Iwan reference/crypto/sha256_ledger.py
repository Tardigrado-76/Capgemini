"""
Immutable Cryptographic Audit Ledger with Ed25519 Digital Attestation.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from .asymmetric_signer import QgradeAsymmetricSigner


def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class QgradeBlock(BaseModel):
    index: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str
    suite_id: str = "Quantigrade - Detalle Iwan"
    payload: dict[str, Any]
    previous_hash: str
    block_hash: str = ""
    ed25519_signature: str | None = None

    @property
    def current_hash(self) -> str:
        return self.block_hash

    @property
    def block_index(self) -> int:
        return self.index

    def calculate_hash(self) -> str:
        canonical_str = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "event_type": self.event_type,
                "suite_id": self.suite_id,
                "payload": self.payload,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )
        return compute_sha256(canonical_str)


class QgradeLedger:
    """Verifiable blockchain ledger with optional Ed25519 signing."""

    def __init__(self, private_key_bytes: bytes | None = None, public_key_bytes: bytes | None = None):
        if private_key_bytes and public_key_bytes:
            self.priv_key = private_key_bytes
            self.pub_key = public_key_bytes
        else:
            self.priv_key, self.pub_key = QgradeAsymmetricSigner.generate_keypair()
        self.chain: list[QgradeBlock] = []
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis = QgradeBlock(
            index=0,
            event_type="GENESIS_INIT",
            payload={"system": "Quantigrade - Detalle Iwan", "standard": "SLSA L3+ / EU AI Act Art. 15"},
            previous_hash="0" * 64,
        )
        genesis.block_hash = genesis.calculate_hash()
        genesis.ed25519_signature = QgradeAsymmetricSigner.sign_hash(self.priv_key, genesis.block_hash)
        self.chain.append(genesis)

    @property
    def latest_block(self) -> QgradeBlock:
        return self.chain[-1]

    def record_event(self, event_type: str, payload: dict[str, Any]) -> QgradeBlock:
        new_block = QgradeBlock(
            index=len(self.chain),
            event_type=event_type,
            payload=payload,
            previous_hash=self.latest_block.block_hash,
        )
        new_block.block_hash = new_block.calculate_hash()
        new_block.ed25519_signature = QgradeAsymmetricSigner.sign_hash(self.priv_key, new_block.block_hash)
        self.chain.append(new_block)
        return new_block

    def verify_integrity(self) -> bool:
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.block_hash != curr.calculate_hash():
                return False
            if curr.previous_hash != prev.block_hash:
                return False
            if curr.ed25519_signature and not QgradeAsymmetricSigner.verify_signature(self.pub_key, curr.block_hash, curr.ed25519_signature):
                return False
        return True

    def verify_chain(self) -> bool:
        """Alias for verify_integrity."""
        return self.verify_integrity()

    def get_hashes(self) -> list[str]:
        return [b.block_hash for b in self.chain]
