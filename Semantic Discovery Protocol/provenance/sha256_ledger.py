"""Discovery Cryptographic Block Ledger.

Provides immutable SHA-256 chained event logging for all capability resolution
and schema hydration operations, ensuring EU AI Act Art. 12 compliance.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class LedgerBlock(BaseModel):
    """Immutable single block in the discovery ledger."""
    index: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str
    payload: dict[str, Any]
    previous_hash: str
    data_hash: str
    block_hash: str
    nonce: int = 0


class DiscoveryLedger:
    """Manages an immutable SHA-256 blockchain ledger for tool resolution."""

    def __init__(self):
        self._chain: list[LedgerBlock] = []
        self._create_genesis_block()

    @property
    def chain(self) -> list[LedgerBlock]:
        return self._chain

    def _create_genesis_block(self):
        genesis_data = {"protocol": "Semantic Discovery Protocol", "version": "1.0.0", "origin": "Genesis"}
        data_str = json.dumps(genesis_data, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        prev_hash = "0" * 64

        raw = f"0:{data_hash}:{prev_hash}:0"
        block_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        genesis = LedgerBlock(
            index=0,
            event_type="GENESIS_SDP",
            payload=genesis_data,
            previous_hash=prev_hash,
            data_hash=data_hash,
            block_hash=block_hash,
            nonce=0,
        )
        self._chain.append(genesis)

    def append_event(self, event_type: str, payload: dict[str, Any]) -> LedgerBlock:
        data_str = json.dumps(payload, sort_keys=True, default=str)
        data_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()

        prev_block = self._chain[-1]
        new_index = prev_block.index + 1
        raw = f"{new_index}:{data_hash}:{prev_block.block_hash}:0"
        block_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

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
        if not self._chain:
            return False

        for i in range(1, len(self._chain)):
            curr = self._chain[i]
            prev = self._chain[i - 1]

            if curr.previous_hash != prev.block_hash:
                return False

            data_str = json.dumps(curr.payload, sort_keys=True, default=str)
            expected_data_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
            if curr.data_hash != expected_data_hash:
                return False

            raw = f"{curr.index}:{curr.data_hash}:{curr.previous_hash}:{curr.nonce}"
            expected_block_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if curr.block_hash != expected_block_hash:
                return False

        return True
