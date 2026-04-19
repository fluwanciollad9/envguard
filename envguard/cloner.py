"""Clone a .env file with optional key filtering and value redaction."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "auth", "pass")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in SENSITIVE_PATTERNS)


@dataclass
class CloneResult:
    original: Dict[str, str]
    cloned: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)
    dropped_keys: List[str] = field(default_factory=list)

    def was_changed(self) -> bool:
        return bool(self.redacted_keys or self.dropped_keys)

    def summary(self) -> str:
        parts = [f"{len(self.cloned)} key(s) cloned"]
        if self.redacted_keys:
            parts.append(f"{len(self.redacted_keys)} redacted")
        if self.dropped_keys:
            parts.append(f"{len(self.dropped_keys)} dropped")
        return ", ".join(parts)


def clone_env(
    env: Dict[str, str],
    *,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    redact_sensitive: bool = False,
    redact_mask: str = "***",
) -> CloneResult:
    redacted: List[str] = []
    dropped: List[str] = []
    cloned: Dict[str, str] = {}

    for key, value in env.items():
        if include is not None and key not in include:
            dropped.append(key)
            continue
        if exclude is not None and key in exclude:
            dropped.append(key)
            continue
        if redact_sensitive and _is_sensitive(key):
            cloned[key] = redact_mask
            redacted.append(key)
        else:
            cloned[key] = value

    return CloneResult(original=dict(env), cloned=cloned, redacted_keys=redacted, dropped_keys=dropped)


def render_cloned(result: CloneResult) -> str:
    lines = [f"{k}={v}" for k, v in result.cloned.items()]
    return "\n".join(lines) + "\n" if lines else ""
