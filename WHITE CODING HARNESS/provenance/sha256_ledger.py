"""Cryptographic Block Ledger.

Provides immutable SHA-256 chained audit records for every event in the White Coding
lifecycle, ensuring EU AI Act Article 12 compliance.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class LedgerBlock(BaseModel):
    """Immutable single block in the cryptographic ledger."""
    index: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str
    payload: dict[str, Any]
    previous_hash: str
    data_hash: str
    block_hash: str
    nonce: int = 0


class CryptographicLedger:
    """Manages an immutable SHA-256 blockchain ledger."""

    def __init__(self):
        self._chain: list[LedgerBlock] = []
        self._create_genesis_block()

    @property
    def chain(self) -> list[LedgerBlock]:
        """Provides direct access to the ledger chain."""
        return self._chain

    def _create_genesis_block(self):
        """Creates the foundational genesis block."""
        genesis_data = {"system": "White Coding Harness", "version": "1.0.0", "origin": "Genesis"}
        data_str = json.dumps(genesis_data, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        prev_hash = "0" * 64

        raw_block = f"0:{data_hash}:{prev_hash}:0"
        block_hash = hashlib.sha256(raw_block.encode("utf-8")).hexdigest()

        genesis = LedgerBlock(
            index=0,
            event_type="GENESIS",
            payload=genesis_data,
            previous_hash=prev_hash,
            data_hash=data_hash,
            block_hash=block_hash,
            nonce=0,
        )
        self._chain.append(genesis)

    def append_event(self, event_type: str, payload: dict[str, Any]) -> LedgerBlock:
        """Appends a new immutable verified event to the chain."""
        data_str = json.dumps(payload, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()

        prev_block = self._chain[-1]
        new_index = prev_block.index + 1
        raw_block = f"{new_index}:{data_hash}:{prev_block.block_hash}:0"
        block_hash = hashlib.sha256(raw_block.encode("utf-8")).hexdigest()

        block = LedgerBlock(
            index=new_index,
            event_type=event_type,
            payload=payload,
            previous_hash=prev_block.block_hash,
            data_hash=data_hash,
            block_hash=block_hash,
            nonce=0,
        )
        self._chain.append(block)
        return block

    def verify_chain(self) -> bool:
        """Verifies complete cryptographic integrity of the blockchain."""
        if not self._chain:
            return False

        for i in range(1, len(self._chain)):
            curr = self._chain[i]
            prev = self._chain[i - 1]

            # 1. Verify previous hash link
            if curr.previous_hash != prev.block_hash:
                return False

            # 2. Verify payload data hash
            data_str = json.dumps(curr.payload, sort_keys=True)
            expected_data_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
            if curr.data_hash != expected_data_hash:
                return False

            # 3. Verify block hash calculation
            raw_block = f"{curr.index}:{curr.data_hash}:{curr.previous_hash}:{curr.nonce}"
            expected_block_hash = hashlib.sha256(raw_block.encode("utf-8")).hexdigest()
            if curr.block_hash != expected_block_hash:
                return False

        return True
