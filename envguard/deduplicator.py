"""Deduplicator: remove duplicate keys from a .env mapping, keeping the last occurrence."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DeduplicateResult:
    env: Dict[str, str]
    duplicates: Dict[str, List[str]]  # key -> list of all values seen (including final)
    order: List[str]  # keys in final order

    def was_changed(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.duplicates:
            return "No duplicate keys found."
        lines = [f"Removed duplicates for {len(self.duplicates)} key(s):"]
        for key, values in self.duplicates.items():
            lines.append(f"  {key}: {len(values)} occurrences, kept last value={self.env[key]!r}")
        return "\n".join(lines)


def deduplicate_env(
    raw_lines: List[str],
    keep: str = "last",
) -> DeduplicateResult:
    """Parse raw .env lines, detect duplicate keys and resolve them.

    Args:
        raw_lines: Lines from a .env file (may include comments/blanks).
        keep: Strategy – 'last' (default) keeps the final value, 'first' keeps the first.

    Returns:
        DeduplicateResult with the deduplicated env mapping.
    """
    seen: Dict[str, List[str]] = {}
    order_first: List[str] = []

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        if key not in seen:
            order_first.append(key)
        seen.setdefault(key, []).append(value)

    duplicates: Dict[str, List[str]] = {
        k: v for k, v in seen.items() if len(v) > 1
    }

    if keep == "first":
        env = {k: v[0] for k, v in seen.items()}
    else:
        env = {k: v[-1] for k, v in seen.items()}

    return DeduplicateResult(env=env, duplicates=duplicates, order=order_first)


def render_deduplicated(result: DeduplicateResult) -> str:
    """Render the deduplicated env as a .env-formatted string."""
    lines = [f"{key}={result.env[key]}" for key in result.order]
    return "\n".join(lines) + ("\n" if lines else "")
