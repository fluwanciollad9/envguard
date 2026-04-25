"""Compare environment variable key prefixes between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set


def _extract_prefix(key: str) -> str:
    """Return the portion of *key* before the first underscore, or the key itself."""
    idx = key.find("_")
    return key[:idx] if idx != -1 else key


def _prefix_map(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Map each prefix to the list of keys that carry it."""
    result: Dict[str, List[str]] = {}
    for key in env:
        prefix = _extract_prefix(key)
        result.setdefault(prefix, []).append(key)
    return result


@dataclass
class PrefixDiffResult:
    source_prefixes: FrozenSet[str]
    target_prefixes: FrozenSet[str]
    only_in_source: FrozenSet[str] = field(default_factory=frozenset)
    only_in_target: FrozenSet[str] = field(default_factory=frozenset)
    common: FrozenSet[str] = field(default_factory=frozenset)
    source_map: Dict[str, List[str]] = field(default_factory=dict)
    target_map: Dict[str, List[str]] = field(default_factory=dict)

    def has_differences(self) -> bool:
        return bool(self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts: List[str] = []
        if self.only_in_source:
            parts.append(f"only in source: {', '.join(sorted(self.only_in_source))}")
        if self.only_in_target:
            parts.append(f"only in target: {', '.join(sorted(self.only_in_target))}")
        if not parts:
            return "prefixes identical"
        return "; ".join(parts)


def diff_prefixes(
    source: Dict[str, str],
    target: Dict[str, str],
) -> PrefixDiffResult:
    """Diff the key-prefix sets of *source* and *target*."""
    src_map = _prefix_map(source)
    tgt_map = _prefix_map(target)
    src_set: Set[str] = set(src_map)
    tgt_set: Set[str] = set(tgt_map)
    return PrefixDiffResult(
        source_prefixes=frozenset(src_set),
        target_prefixes=frozenset(tgt_set),
        only_in_source=frozenset(src_set - tgt_set),
        only_in_target=frozenset(tgt_set - src_set),
        common=frozenset(src_set & tgt_set),
        source_map=src_map,
        target_map=tgt_map,
    )
