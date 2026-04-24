"""Key rotation: rename keys according to a rotation map and redact old values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RotateResult:
    original: Dict[str, str]
    rotated: Dict[str, str]
    renamed: List[tuple]   # (old_key, new_key)
    not_found: List[str]   # old keys absent from env
    conflicts: List[str]   # new keys that already existed


def was_changed(result: RotateResult) -> bool:
    return bool(result.renamed)


def summary(result: RotateResult) -> str:
    parts = [f"{len(result.renamed)} key(s) rotated"]
    if result.not_found:
        parts.append(f"{len(result.not_found)} not found")
    if result.conflicts:
        parts.append(f"{len(result.conflicts)} conflict(s) skipped")
    return ", ".join(parts)


def rotate_env(
    env: Dict[str, str],
    rotation_map: Dict[str, str],
    overwrite_conflicts: bool = False,
) -> RotateResult:
    """Rename keys according to rotation_map.

    rotation_map: {old_key: new_key}
    If new_key already exists and overwrite_conflicts is False the rename is skipped.
    """
    rotated = dict(env)
    renamed: List[tuple] = []
    not_found: List[str] = []
    conflicts: List[str] = []

    for old_key, new_key in rotation_map.items():
        if old_key not in rotated:
            not_found.append(old_key)
            continue
        if new_key in rotated and not overwrite_conflicts:
            conflicts.append(new_key)
            continue
        value = rotated.pop(old_key)
        rotated[new_key] = value
        renamed.append((old_key, new_key))

    return RotateResult(
        original=dict(env),
        rotated=rotated,
        renamed=renamed,
        not_found=not_found,
        conflicts=conflicts,
    )


def render_rotated(result: RotateResult) -> str:
    lines = []
    for key, value in result.rotated.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
