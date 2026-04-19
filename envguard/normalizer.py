"""Normalize .env values: uppercase keys, strip whitespace, standardize booleans."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)

    def was_changed(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        if not self.changes:
            return "No normalization changes."
        lines = [f"{len(self.changes)} change(s):"]
        for key, old, new in self.changes:
            lines.append(f"  {key}: {old!r} -> {new!r}")
        return "\n".join(lines)


def normalize_env(
    env: Dict[str, str],
    *,
    uppercase_keys: bool = True,
    strip_values: bool = True,
    normalize_bools: bool = True,
) -> NormalizeResult:
    """Return a NormalizeResult with normalized keys/values."""
    original = dict(env)
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        new_key = key.upper() if uppercase_keys else key
        new_value = value.strip() if strip_values else value

        if normalize_bools:
            lower = new_value.lower()
            if lower in _BOOL_TRUE:
                new_value = "true"
            elif lower in _BOOL_FALSE:
                new_value = "false"

        if new_key != key or new_value != value:
            changes.append((new_key, value, new_value))

        normalized[new_key] = new_value

    return NormalizeResult(original=original, normalized=normalized, changes=changes)


def render_normalized(result: NormalizeResult) -> str:
    """Render normalized env as .env file content."""
    lines = [f"{k}={v}" for k, v in result.normalized.items()]
    return "\n".join(lines) + ("\n" if lines else "")
