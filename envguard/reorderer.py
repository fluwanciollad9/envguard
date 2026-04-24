"""Reorder .env keys according to a specified key order list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReorderResult:
    original: Dict[str, str]
    reordered: Dict[str, str]
    order_applied: List[str]
    unrecognised: List[str] = field(default_factory=list)  # keys not in order list
    missing: List[str] = field(default_factory=list)       # order keys absent from env

    def was_changed(self) -> bool:
        return list(self.original.keys()) != list(self.reordered.keys())

    def summary(self) -> str:
        parts = [f"{len(self.reordered)} keys reordered"]
        if self.unrecognised:
            parts.append(f"{len(self.unrecognised)} key(s) appended (not in order list)")
        if self.missing:
            parts.append(f"{len(self.missing)} order key(s) not present in env")
        return "; ".join(parts)


def reorder_env(
    env: Dict[str, str],
    order: List[str],
    append_unrecognised: bool = True,
) -> ReorderResult:
    """Return a new env dict with keys arranged according to *order*.

    Keys present in *env* but absent from *order* are appended at the end
    when *append_unrecognised* is True, otherwise they are dropped.
    """
    order_set = dict.fromkeys(order)  # preserves insertion order, O(1) lookup
    reordered: Dict[str, str] = {}

    for key in order:
        if key in env:
            reordered[key] = env[key]

    unrecognised: List[str] = [k for k in env if k not in order_set]
    if append_unrecognised:
        for key in unrecognised:
            reordered[key] = env[key]

    missing: List[str] = [k for k in order if k not in env]

    return ReorderResult(
        original=dict(env),
        reordered=reordered,
        order_applied=list(order),
        unrecognised=unrecognised,
        missing=missing,
    )


def render_reordered(result: ReorderResult) -> str:
    """Render the reordered env dict as a .env-formatted string."""
    lines = [f"{k}={v}" for k, v in result.reordered.items()]
    return "\n".join(lines) + ("\n" if lines else "")
