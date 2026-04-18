"""Merge multiple .env files with precedence rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class MergeResult:
    merged: Dict[str, str]
    overrides: List[Tuple[str, str, str, str]] = field(default_factory=list)
    # (key, old_source, new_source, new_value)

    @property
    def override_count(self) -> int:
        return len(self.overrides)


def merge_envs(sources: List[Tuple[str, Dict[str, str]]]) -> MergeResult:
    """Merge env dicts in order; later sources override earlier ones.

    Args:
        sources: list of (label, env_dict) pairs in ascending priority order.

    Returns:
        MergeResult with the final merged dict and a log of overrides.
    """
    merged: Dict[str, str] = {}
    key_source: Dict[str, str] = {}
    overrides: List[Tuple[str, str, str, str]] = []

    for label, env in sources:
        for key, value in env.items():
            if key in merged:
                overrides.append((key, key_source[key], label, value))
            merged[key] = value
            key_source[key] = label

    return MergeResult(merged=merged, overrides=overrides)
