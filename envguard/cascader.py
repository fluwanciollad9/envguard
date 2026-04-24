"""Cascade multiple .env files, with later files taking precedence.

Like merger.py but tracks the origin (source file index) of each key.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CascadeResult:
    """Result of cascading several env mappings together."""

    env: Dict[str, str]
    # key -> (value, source_index)
    origins: Dict[str, Tuple[str, int]] = field(default_factory=dict)
    override_count: int = 0

    def source_for(self, key: str) -> int:
        """Return the index of the source file that supplied *key*."""
        return self.origins[key][1]

    def summary(self) -> str:
        total = len(self.env)
        return (
            f"{total} key(s) in cascaded env; "
            f"{self.override_count} override(s) applied"
        )


def cascade_envs(sources: List[Dict[str, str]]) -> CascadeResult:
    """Cascade *sources* left-to-right; later entries win.

    Args:
        sources: Ordered list of env dicts (index 0 = lowest priority).

    Returns:
        A :class:`CascadeResult` with the merged env and provenance data.
    """
    env: Dict[str, str] = {}
    origins: Dict[str, Tuple[str, int]] = {}
    override_count = 0

    for idx, source in enumerate(sources):
        for key, value in source.items():
            if key in env:
                override_count += 1
            env[key] = value
            origins[key] = (value, idx)

    return CascadeResult(env=env, origins=origins, override_count=override_count)
