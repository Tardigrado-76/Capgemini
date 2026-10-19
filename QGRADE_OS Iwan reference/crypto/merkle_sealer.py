"""
Binary Merkle Tree Implementation with Signed Attestation for Quantigrade.
"""

from __future__ import annotations

import hashlib

from pydantic import BaseModel

from .asymmetric_signer import QgradeAsymmetricSigner


def hash_pair(left: str, right: str) -> str:
    combined = (left + right).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


class QgradeMerkleProof(BaseModel):
    leaf_hash: str
    root_hash: str
    audit_path: list[tuple[str, str]]
    signed_root: str | None = None


class QgradeMerkleTree:
    """Computes a balanced binary Merkle tree over arbitrary string evidence hashes."""

    def __init__(self, leaves: list[str], signing_key: bytes | None = None):
        if not leaves:
            raise ValueError("Cannot construct Merkle tree with empty leaves.")
        self.leaves = [l if len(l) == 64 else hashlib.sha256(l.encode("utf-8")).hexdigest() for l in leaves]
        self.levels: list[list[str]] = [self.leaves]
        self.signing_key = signing_key
        self._build_tree()

    def _build_tree(self) -> None:
        current_level = self.leaves
        while len(current_level) > 1:
            next_level: list[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left
                parent = hash_pair(left, right)
                next_level.append(parent)
            self.levels.append(next_level)
            current_level = next_level

    @property
    def root(self) -> str:
        return self.levels[-1][0]

    @property
    def root_hash(self) -> str:
        return self.root

    def get_signed_root(self) -> str | None:
        if not self.signing_key:
            return None
        return QgradeAsymmetricSigner.sign_hash(self.signing_key, self.root)

    def get_proof(self, leaf_index: int) -> QgradeMerkleProof:
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError("Leaf index out of bounds.")

        leaf_hash = self.leaves[leaf_index]
        audit_path: list[tuple[str, str]] = []
        idx = leaf_index

        for level in self.levels[:-1]:
            is_right_child = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right_child else idx + 1
            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                sibling_hash = level[idx]

            direction = "L" if is_right_child else "R"
            audit_path.append((direction, sibling_hash))
            idx //= 2

        signed_root = self.get_signed_root()
        return QgradeMerkleProof(leaf_hash=leaf_hash, root_hash=self.root, audit_path=audit_path, signed_root=signed_root)

    @staticmethod
    def verify_proof(proof: QgradeMerkleProof) -> bool:
        current = proof.leaf_hash
        for direction, sibling in proof.audit_path:
            if direction == "L":
                current = hash_pair(sibling, current)
            else:
                current = hash_pair(current, sibling)
        return current == proof.root_hash
