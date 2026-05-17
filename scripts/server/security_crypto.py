"""Utilities for authenticated encryption of sensitive values at rest."""

import base64
import hashlib
import os
from typing import Optional


def _resolve_master_key() -> bytes:
    """Resolve a stable 32-byte key for AES-GCM operations."""
    key_b64 = os.getenv("SECURITY_ENCRYPTION_KEY")
    if key_b64:
        try:
            raw = base64.urlsafe_b64decode(key_b64.encode("utf-8"))
            if len(raw) >= 32:
                return raw[:32]
        except Exception:
            pass

    seed = os.getenv("SECRET_KEY", "phiversity-default-security-seed")
    return hashlib.sha256(seed.encode("utf-8")).digest()


def encrypt_text(plaintext: str) -> str:
    """Encrypt text using AES-256-GCM; output is URL-safe base64 payload."""
    if plaintext is None:
        return ""

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = _resolve_master_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_text(ciphertext_b64: str) -> str:
    """Decrypt URL-safe base64 AES-256-GCM payload back to plaintext."""
    if not ciphertext_b64:
        return ""

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    blob = base64.urlsafe_b64decode(ciphertext_b64.encode("utf-8"))
    nonce = blob[:12]
    ciphertext = blob[12:]
    aesgcm = AESGCM(_resolve_master_key())
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
