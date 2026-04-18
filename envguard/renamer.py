"""Rename keys across a .env file with optional dry-run support."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RenameResult:
    original: Dict[str, str]
    renamed: Dict[str, str]
    changes: List[Tuple[str, str]] = field(default_factory=list)  # (old, new)
    not_found: List[str] = field(default_factory=list)


def was_changed(result: RenameResult) -> bool:
    return len(result.changes) > 0


def rename_env(
    env: Dict[str, str],
    renames: Dict[str, str],  # {old_key: new_key}
) -> RenameResult:
    """Return a new env dict with keys renamed according to the mapping."""
    renamed: Dict[str, str] = {}
    changes: List[Tuple[str, str]] = []
    not_found: List[str] = []

    applied: set = set()
    for key, value in env.items():
        if key in renames:
            new_key = renames[key]
            renamed[new_key] = value
            changes.append((key, new_key))
            applied.add(key)
        else:
            renamed[key] = value

    for old_key in renames:
        if old_key not in applied:
            not_found.append(old_key)

    return RenameResult(original=env, renamed=renamed, changes=changes, not_found=not_found)


def render_renamed(result: RenameResult) -> str:
    """Render the renamed env as a .env formatted string."""
    lines = [f"{k}={v}" for k, v in result.renamed.items()]
    return "\n".join(lines) + ("\n" if lines else "")
