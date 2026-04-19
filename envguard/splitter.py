"""Split a .env file into multiple files based on key prefixes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SplitResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def total_keys(self) -> int:
        return sum(len(v) for v in self.groups.values()) + len(self.ungrouped)

    def summary(self) -> str:
        parts = [f"{name}: {len(keys)} key(s)" for name, keys in sorted(self.groups.items())]
        if self.ungrouped:
            parts.append(f"ungrouped: {len(self.ungrouped)} key(s)")
        return ", ".join(parts) if parts else "no keys"


def split_env(
    env: Dict[str, str],
    prefixes: List[str],
    *,
    case_sensitive: bool = False,
    strip_prefix: bool = False,
) -> SplitResult:
    """Split env into groups by prefix. Keys not matching any prefix go to ungrouped."""
    result = SplitResult()

    normalised = [
        (p if case_sensitive else p.upper()) for p in prefixes
    ]

    for key, value in env.items():
        compare_key = key if case_sensitive else key.upper()
        matched = False
        for raw_prefix, norm_prefix in zip(prefixes, normalised):
            if compare_key.startswith(norm_prefix):
                group_name = raw_prefix.rstrip("_").upper()
                out_key = key[len(raw_prefix):] if strip_prefix else key
                result.groups.setdefault(group_name, {})[out_key] = value
                matched = True
                break
        if not matched:
            result.ungrouped[key] = value

    return result


def render_split(env: Dict[str, str]) -> str:
    """Render a dict back to .env format."""
    lines = [f"{k}={v}" for k, v in env.items()]
    return "\n".join(lines) + ("\n" if lines else "")
