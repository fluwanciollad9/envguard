"""Flatten nested prefixes into a single-level .env dict.

Given a dict and a separator (default '__'), keys like
  DB__HOST=localhost
  DB__PORT=5432
are returned as-is but grouped under their common prefix.
The module also provides the inverse: expand a flat key back
into a nested representation (as a plain dict-of-dicts).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    env: Dict[str, str]
    groups: Dict[str, List[str]]  # prefix -> [keys]
    separator: str
    ungrouped: List[str] = field(default_factory=list)

    def group_count(self) -> int:
        return len(self.groups)

    def was_grouped(self) -> bool:
        return bool(self.groups)

    def summary(self) -> str:
        parts = [f"{len(self.env)} keys total"]
        if self.groups:
            parts.append(f"{self.group_count()} prefix group(s)")
        if self.ungrouped:
            parts.append(f"{len(self.ungrouped)} ungrouped")
        return ", ".join(parts)


def flatten_env(
    env: Dict[str, str],
    separator: str = "__",
    prefixes: Optional[List[str]] = None,
) -> FlattenResult:
    """Group keys by their prefix (everything before the first separator).

    If *prefixes* is given only those prefixes are considered; all other
    keys land in *ungrouped*.
    """
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for key in env:
        if separator in key:
            prefix = key.split(separator, 1)[0]
            if prefixes is None or prefix.upper() in [p.upper() for p in prefixes]:
                groups.setdefault(prefix, []).append(key)
                continue
        ungrouped.append(key)

    return FlattenResult(
        env=dict(env),
        groups=groups,
        separator=separator,
        ungrouped=ungrouped,
    )


def expand_env(env: Dict[str, str], separator: str = "__") -> Dict:
    """Expand flat env keys into a nested dict structure.

    DB__HOST=localhost  ->  {"DB": {"HOST": "localhost"}}
    Keys without the separator become top-level string values.
    """
    result: Dict = {}
    for key, value in env.items():
        if separator in key:
            parts = key.split(separator)
            node = result
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value
        else:
            result[key] = value
    return result
