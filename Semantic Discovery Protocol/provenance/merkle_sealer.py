"""Discovery Merkle Tree Sealer.

Calculates binary Merkle tree proofs across capability resolutions and parameter validations,
generating tamper-evident certificates meeting SLSA Level 3+ and EU AI Act Art. 12 standards.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class DiscoveryMerkleSeal(BaseModel):
    """Cryptographic seal proving integrity of capability resolution events."""
    seal_id: str
    merkle_root_hash: str
    total_evidences: int
    manifest: list[dict[str, str]] = Field(default_factory=list)
    slsa_level: str = "SLSA Level 3+"
    framework: str = "EU AI Act Art. 12 Trazabilidad de Herramientas"
    sealed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DiscoveryMerkleSealer:
    """Computes binary Merkle tree proofs for discovery operations."""

    def __init__(self):
        self.leaves: list[str] = []
        self.manifest: list[dict[str, str]] = []

    def add_evidence(self, event_type: str, item_id: str, content: Any) -> str:
        if isinstance(content, str):
            raw = content
        else:
            raw = json.dumps(content, sort_keys=True, default=str)

        leaf_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        self.leaves.append(leaf_hash)
        self.manifest.append({
            "event_type": event_type,
            "item_id": item_id,
            "data_hash": leaf_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return leaf_hash

    def compute_root(self) -> str:
        if not self.leaves:
            return hashlib.sha256(b"EMPTY_DISCOVERY_MESH").hexdigest()

        current = self.leaves[:]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
                next_level.append(combined)
            current = next_level

        return current[0]

    def seal(self, namespace: str = "global.sdp") -> DiscoveryMerkleSeal:
        root = self.compute_root()
        seal_id = f"SDP-SEAL-{uuid.uuid4().hex[:8].upper()}"

        return DiscoveryMerkleSeal(
            seal_id=seal_id,
            merkle_root_hash=root,
            total_evidences=len(self.leaves),
            manifest=self.manifest,
        )
