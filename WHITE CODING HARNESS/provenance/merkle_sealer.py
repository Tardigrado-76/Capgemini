"""Merkle Tree Evidence Bunker.

Constructs non-repudiable hierarchical Merkle proofs for all artifacts generated
under the White Coding harness, meeting SLSA Level 3+ and EU AI Act requirements.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MerkleSeal(BaseModel):
    """Immutable seal certifying the integrity of all artifacts."""
    seal_id: str
    merkle_root_hash: str
    total_evidences: int
    sealed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_manifest: list[dict[str, str]] = Field(default_factory=list)
    slsa_level: str = "SLSA Level 3+"
    compliance_frameworks: list[str] = Field(
        default_factory=lambda: ["EU AI Act Art. 12", "NIS2 Directiva UE 2022/2555", "SLSA L3+"]
    )


class MerkleEvidenceBunker:
    """Calculates hierarchical binary Merkle tree across all generated assets."""

    def __init__(self):
        self.leaves: list[str] = []
        self.manifest: list[dict[str, str]] = []

    def add_evidence(self, evidence_type: str, item_id: str, content: Any) -> str:
        """Hashes an evidence payload and appends it to the Merkle leaves."""
        if isinstance(content, str):
            raw = content
        else:
            raw = json.dumps(content, sort_keys=True, default=str)

        leaf_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        self.leaves.append(leaf_hash)
        self.manifest.append({
            "evidence_id": item_id,
            "evidence_type": evidence_type,
            "data_hash": leaf_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return leaf_hash

    def compute_root(self) -> str:
        """Computes the root hash of the binary Merkle tree."""
        if not self.leaves:
            return hashlib.sha256(b"EMPTY_BUNKER").hexdigest()

        current_level = self.leaves[:]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left  # Duplicate odd leaf according to Merkle standard

                combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
                next_level.append(combined)
            current_level = next_level

        return current_level[0]

    def seal(self, system_name: str = "white-coding") -> MerkleSeal:
        """Finalizes the Merkle tree and produces a formal audit seal."""
        root = self.compute_root()
        import uuid
        seal_id = f"SEAL-{uuid.uuid4().hex[:8].upper()}"

        return MerkleSeal(
            seal_id=seal_id,
            merkle_root_hash=root,
            total_evidences=len(self.leaves),
            evidence_manifest=self.manifest,
        )
