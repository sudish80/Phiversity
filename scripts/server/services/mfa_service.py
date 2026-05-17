"""TOTP MFA utilities and backup code management."""

import base64
import hmac
import json
import os
import secrets
import struct
import time
from hashlib import sha1, sha256
from typing import List

from ..security_crypto import encrypt_text, decrypt_text


class MFAService:
    """Service for generating and verifying TOTP MFA credentials."""

    @staticmethod
    def generate_secret(length: int = 20) -> str:
        raw = secrets.token_bytes(length)
        return base64.b32encode(raw).decode("utf-8").rstrip("=")

    @staticmethod
    def _totp_code(secret_b32: str, timestamp: int, period: int = 30, digits: int = 6) -> str:
        normalized = secret_b32.upper()
        pad = "=" * ((8 - (len(normalized) % 8)) % 8)
        key = base64.b32decode(normalized + pad)
        counter = int(timestamp // period)
        msg = struct.pack(">Q", counter)
        digest = hmac.new(key, msg, sha1).digest()
        offset = digest[-1] & 0x0F
        binary = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
        code = binary % (10**digits)
        return str(code).zfill(digits)

    @staticmethod
    def verify_totp(secret_b32: str, code: str, window: int = 1) -> bool:
        if not code or not code.isdigit() or len(code) not in {6, 8}:
            return False

        now = int(time.time())
        for step in range(-window, window + 1):
            expected = MFAService._totp_code(secret_b32, now + (step * 30), digits=len(code))
            if hmac.compare_digest(expected, code):
                return True
        return False

    @staticmethod
    def provisioning_uri(secret_b32: str, email: str, issuer: str = "Phiversity") -> str:
        safe_issuer = issuer.replace(" ", "%20")
        safe_email = email.replace("@", "%40")
        return f"otpauth://totp/{safe_issuer}:{safe_email}?secret={secret_b32}&issuer={safe_issuer}&algorithm=SHA1&digits=6&period=30"

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        codes: List[str] = []
        for _ in range(count):
            part1 = secrets.token_hex(2).upper()
            part2 = secrets.token_hex(2).upper()
            codes.append(f"{part1}-{part2}")
        return codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        return sha256(code.encode("utf-8")).hexdigest()

    @staticmethod
    def encrypt_secret(secret: str) -> str:
        return encrypt_text(secret)

    @staticmethod
    def decrypt_secret(secret_encrypted: str) -> str:
        return decrypt_text(secret_encrypted)

    @staticmethod
    def encode_backup_hashes(hashes: List[str]) -> str:
        return encrypt_text(json.dumps(hashes))

    @staticmethod
    def decode_backup_hashes(payload: str) -> List[str]:
        if not payload:
            return []
        decoded = decrypt_text(payload)
        try:
            data = json.loads(decoded)
            return data if isinstance(data, list) else []
        except Exception:
            return []
