"""aliaser.py – map keys to canonical aliases within a .env environment."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasResult:
    """Result of applying an alias map to an env dict."""

    env: Dict[str, str]
    """The resulting environment with aliases applied."""

    applied: List[str] = field(default_factory=list)
    """Alias keys that were successfully written."""

    skipped: List[str] = field(default_factory=list)
    """Alias keys skipped because the source key was absent."""

    conflicts: List[str] = field(default_factory=list)
    """Alias keys skipped because the target already existed and overwrite=False."""


def was_changed(result: AliasResult) -> bool:
    """Return True if any alias was applied to the environment."""
    return bool(result.applied)


def summary(result: AliasResult) -> str:
    """Return a human-readable one-line summary of the alias operation."""
    parts = [f"{len(result.applied)} applied"]
    if result.skipped:
        parts.append(f"{len(result.skipped)} skipped (source absent)")
    if result.conflicts:
        parts.append(f"{len(result.conflicts)} conflict(s) not overwritten")
    return ", ".join(parts)


def alias_env(
    env: Dict[str, str],
    alias_map: Dict[str, str],
    *,
    overwrite: bool = False,
    keep_original: bool = True,
) -> AliasResult:
    """Apply *alias_map* to *env*, creating new keys from existing ones.

    Parameters
    ----------
    env:
        Source environment dictionary.
    alias_map:
        Mapping of ``{source_key: alias_key}``.
    overwrite:
        If *True*, overwrite the alias key even when it already exists.
    keep_original:
        If *True* (default), the original source key is preserved alongside
        the alias.  Set to *False* to remove the source key after aliasing.
    """
    result_env: Dict[str, str] = dict(env)
    applied: List[str] = []
    skipped: List[str] = []
    conflicts: List[str] = []

    for source_key, alias_key in alias_map.items():
        if source_key not in result_env:
            skipped.append(source_key)
            continue

        if alias_key in result_env and not overwrite:
            conflicts.append(alias_key)
            continue

        result_env[alias_key] = result_env[source_key]
        applied.append(alias_key)

        if not keep_original:
            result_env.pop(source_key, None)

    return AliasResult(
        env=result_env,
        applied=applied,
        skipped=skipped,
        conflicts=conflicts,
    )
