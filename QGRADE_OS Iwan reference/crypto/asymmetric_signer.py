"""Ed25519 Asymmetric Digital Signatures for Cryptographic Audit Integrity.

Eliminates unilateral local hash forgery by signing Merkle roots and ledger blocks.
"""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


class QgradeAsymmetricSigner:
    """Manages Ed25519 signing and verification for Quantigrade audit trails."""

    def __init__(self, private_bytes: bytes | None = None):
        if private_bytes:
            self._priv_bytes = private_bytes
            priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
            self._pub_bytes = priv_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        else:
            self._priv_bytes, self._pub_bytes = self.generate_keypair()

    @property
    def public_bytes(self) -> bytes:
        return self._pub_bytes

    @property
    def private_bytes(self) -> bytes:
        return self._priv_bytes

    def public_key_hex(self) -> str:
        return self._pub_bytes.hex()

    def private_key_hex(self) -> str:
        return self._priv_bytes.hex()

    def sign_payload(self, text: str) -> str:
        return self.sign_hash(self._priv_bytes, text)

    def verify_payload(self, text: str, signature_hex: str, public_key_hex: str | None = None) -> bool:
        pub_bytes = bytes.fromhex(public_key_hex) if public_key_hex else self._pub_bytes
        return self.verify_signature(pub_bytes, text, signature_hex)

    @classmethod
    def generate_keypair(cls) -> tuple[bytes, bytes]:
        """Generates raw (private_key_bytes, public_key_bytes)."""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return priv_bytes, pub_bytes

    @classmethod
    def sign_hash(cls, private_key_bytes: bytes, data_hash: str) -> str:
        """Signs a hexadecimal hash string and returns the hex signature."""
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        signature = private_key.sign(data_hash.encode("utf-8"))
        return signature.hex()

    @classmethod
    def verify_signature(cls, public_key_bytes: bytes, data_hash: str, signature_hex: str) -> bool:
        """Verifies if signature matches data_hash under the public key."""
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature_bytes = bytes.fromhex(signature_hex)
            public_key.verify(signature_bytes, data_hash.encode("utf-8"))
            return True
        except (InvalidSignature, ValueError, TypeError, RuntimeError, OSError):
            return False
