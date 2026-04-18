"""Redact sensitive values from env dicts before printing or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SECRET_PATTERNS = (
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "API_KEY",
    "PRIVATE_KEY",
    "AUTH",
    "CREDENTIAL",
)

REDACTED = "***REDACTED***"


@dataclass
class RedactResult:
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(pat in upper for pat in _SECRET_PATTERNS)


def redact_env(
    env: Dict[str, str],
    extra_patterns: List[str] | None = None,
    show_partial: bool = False,
) -> RedactResult:
    """Return a copy of *env* with sensitive values replaced by REDACTED.

    Args:
        env: Parsed env mapping.
        extra_patterns: Additional substrings that mark a key as sensitive.
        show_partial: If True, reveal first 4 chars of value instead of full mask.
    """
    patterns = list(_SECRET_PATTERNS) + [p.upper() for p in (extra_patterns or [])]
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        upper = key.upper()
        if any(pat in upper for pat in patterns):
            if show_partial and len(value) > 4:
                masked = value[:4] + "*" * (len(value) - 4)
            else:
                masked = REDACTED
            redacted[key] = masked
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(redacted=redacted, redacted_keys=sorted(redacted_keys))
