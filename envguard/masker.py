"""Mask sensitive values in an env dict, replacing with a fixed pattern."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_SUBSTRINGS = ("password", "secret", "token", "api_key", "apikey", "private", "auth", "credential")
DEFAULT_MASK = "********"


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(s in lower for s in _SENSITIVE_SUBSTRINGS)


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    def was_masked(self) -> bool:
        return len(self.masked_keys) > 0

    def summary(self) -> str:
        if not self.was_masked():
            return "No sensitive keys found."
        keys = ", ".join(self.masked_keys)
        return f"{len(self.masked_keys)} key(s) masked: {keys}"


def mask_env(env: Dict[str, str], mask: str = DEFAULT_MASK, keys: List[str] | None = None) -> MaskResult:
    """Return a copy of env with sensitive values replaced by mask.

    If *keys* is provided those keys are masked regardless of name heuristics.
    """
    explicit = set(keys or [])
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for k, v in env.items():
        if k in explicit or _is_sensitive(k):
            masked[k] = mask
            masked_keys.append(k)
        else:
            masked[k] = v

    return MaskResult(original=dict(env), masked=masked, masked_keys=sorted(masked_keys))
