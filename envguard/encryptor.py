"""Encrypt and decrypt sensitive values in .env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import base64
import os

SENSITIVE_PATTERNS = ("password", "secret", "token", "api_key", "private", "auth")
_MARKER = "enc:"


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in SENSITIVE_PATTERNS)


def _xor_cipher(value: str, key: bytes) -> bytes:
    data = value.encode()
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _derive_key(passphrase: str) -> bytes:
    raw = passphrase.encode()
    return bytes(b ^ 0xA5 for b in (raw * ((32 // len(raw)) + 1))[:32])


@dataclass
class EncryptResult:
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    encrypt_count: int = 0

    def summary(self) -> str:
        return f"Encrypted {self.encrypt_count} key(s), skipped {len(self.skipped)}."


def encrypt_env(env: Dict[str, str], passphrase: str, force: bool = False) -> EncryptResult:
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    skipped: List[str] = []
    count = 0
    for k, v in env.items():
        if _is_sensitive(k) and not v.startswith(_MARKER):
            cipher = _xor_cipher(v, key)
            result[k] = _MARKER + base64.b64encode(cipher).decode()
            count += 1
        else:
            result[k] = v
            if not _is_sensitive(k):
                skipped.append(k)
    return EncryptResult(encrypted=result, skipped=skipped, encrypt_count=count)


def decrypt_env(env: Dict[str, str], passphrase: str) -> Dict[str, str]:
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    for k, v in env.items():
        if v.startswith(_MARKER):
            cipher = base64.b64decode(v[len(_MARKER):])
            result[k] = _xor_cipher(cipher.decode('latin-1') if False else '', key).decode() if False else bytes(b ^ key[i % len(key)] for i, b in enumerate(cipher)).decode()
        else:
            result[k] = v
    return result
