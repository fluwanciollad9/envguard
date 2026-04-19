"""Strip specified keys from an env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StripResult:
    original: Dict[str, str]
    stripped: Dict[str, str]
    removed: List[str] = field(default_factory=list)
    not_found: List[str] = field(default_factory=list)

    def was_changed(self) -> bool:
        return len(self.removed) > 0

    def summary(self) -> str:
        parts = []
        if self.removed:
            parts.append(f"removed {len(self.removed)} key(s): {', '.join(self.removed)}")
        if self.not_found:
            parts.append(f"{len(self.not_found)} key(s) not found: {', '.join(self.not_found)}")
        if not parts:
            return "nothing to strip"
        return "; ".join(parts)


def strip_env(env: Dict[str, str], keys: List[str]) -> StripResult:
    """Return a new env dict with the given keys removed."""
    removed: List[str] = []
    not_found: List[str] = []

    result = dict(env)
    for key in keys:
        if key in result:
            del result[key]
            removed.append(key)
        else:
            not_found.append(key)

    return StripResult(
        original=dict(env),
        stripped=result,
        removed=removed,
        not_found=not_found,
    )


def render_stripped(stripped: Dict[str, str]) -> str:
    lines = [f"{k}={v}" for k, v in stripped.items()]
    return "\n".join(lines) + ("\n" if lines else "")
