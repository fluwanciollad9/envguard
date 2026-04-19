"""Patch (find-and-replace values) across a parsed .env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class PatchResult:
    original: Dict[str, str]
    patched: Dict[str, str]
    applied: List[Tuple[str, str, str]] = field(default_factory=list)   # (key, old, new)
    not_found: List[str] = field(default_factory=list)

    def was_changed(self) -> bool:
        return len(self.applied) > 0

    def summary(self) -> str:
        parts = [f"{len(self.applied)} patch(es) applied"]
        if self.not_found:
            parts.append(f"{len(self.not_found)} key(s) not found")
        return ", ".join(parts)


def patch_env(
    env: Dict[str, str],
    patches: Dict[str, str],
) -> PatchResult:
    """Apply *patches* (key -> new_value) to *env*.

    Keys present in *patches* but absent from *env* are recorded in
    ``not_found``; they are **not** inserted.
    """
    patched = dict(env)
    applied: List[Tuple[str, str, str]] = []
    not_found: List[str] = []

    for key, new_value in patches.items():
        if key in patched:
            old_value = patched[key]
            patched[key] = new_value
            applied.append((key, old_value, new_value))
        else:
            not_found.append(key)

    return PatchResult(
        original=env,
        patched=patched,
        applied=applied,
        not_found=not_found,
    )


def render_patched(result: PatchResult) -> str:
    """Render the patched env as .env file text."""
    lines = [f"{k}={v}" for k, v in result.patched.items()]
    return "\n".join(lines) + ("\n" if lines else "")
