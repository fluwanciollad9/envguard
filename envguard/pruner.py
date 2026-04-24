"""Remove keys from an env dict whose values match a given pattern or condition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class PruneResult:
    original: Dict[str, str]
    pruned: Dict[str, str]
    removed: List[str] = field(default_factory=list)
    pattern: Optional[str] = None

    def was_changed(self) -> bool:
        return len(self.removed) > 0

    def summary(self) -> str:
        if not self.removed:
            return "No keys pruned."
        keys = ", ".join(self.removed)
        return f"Pruned {len(self.removed)} key(s): {keys}"


def prune_env(
    env: Dict[str, str],
    *,
    pattern: Optional[str] = None,
    empty_only: bool = False,
    keys: Optional[List[str]] = None,
) -> PruneResult:
    """Remove keys matching the given criteria.

    Priority: explicit *keys* list > *pattern* regex > *empty_only* flag.
    At least one criterion must be provided.
    """
    if keys is None and pattern is None and not empty_only:
        raise ValueError("Provide at least one of: keys, pattern, or empty_only=True")

    removed: List[str] = []
    result: Dict[str, str] = {}

    compiled = re.compile(pattern) if pattern else None

    for k, v in env.items():
        drop = False
        if keys is not None and k in keys:
            drop = True
        elif compiled is not None and compiled.search(v):
            drop = True
        elif empty_only and v == "":
            drop = True

        if drop:
            removed.append(k)
        else:
            result[k] = v

    return PruneResult(
        original=dict(env),
        pruned=result,
        removed=removed,
        pattern=pattern,
    )


def render_pruned(pruned: Dict[str, str]) -> str:
    lines = [f"{k}={v}" for k, v in pruned.items()]
    return "\n".join(lines) + ("\n" if lines else "")
