"""Detect keys whose names differ only in case between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CaseDiffEntry:
    source_key: str
    target_key: str

    def __str__(self) -> str:
        return f"{self.source_key!r} -> {self.target_key!r}"


@dataclass
class CaseDiffResult:
    case_conflicts: List[CaseDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.case_conflicts or self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts: List[str] = []
        if self.case_conflicts:
            parts.append(f"{len(self.case_conflicts)} case conflict(s)")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} only in source")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} only in target")
        return ", ".join(parts) if parts else "no case differences"


def _lower_map(env: Dict[str, str]) -> Dict[str, str]:
    """Return mapping of lowercased key -> original key."""
    result: Dict[str, str] = {}
    for k in env:
        result[k.lower()] = k
    return result


def diff_case(
    source: Dict[str, str],
    target: Dict[str, str],
) -> CaseDiffResult:
    """Compare two envs and report keys that differ only in case."""
    src_lower = _lower_map(source)
    tgt_lower = _lower_map(target)

    conflicts: List[CaseDiffEntry] = []
    only_source: List[str] = []
    only_target: List[str] = []

    all_lower = set(src_lower) | set(tgt_lower)
    for lk in sorted(all_lower):
        in_src = lk in src_lower
        in_tgt = lk in tgt_lower
        if in_src and in_tgt:
            sk = src_lower[lk]
            tk = tgt_lower[lk]
            if sk != tk:
                conflicts.append(CaseDiffEntry(source_key=sk, target_key=tk))
        elif in_src:
            only_source.append(src_lower[lk])
        else:
            only_target.append(tgt_lower[lk])

    return CaseDiffResult(
        case_conflicts=conflicts,
        only_in_source=only_source,
        only_in_target=only_target,
    )
