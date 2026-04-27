"""Diff whitespace characteristics between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class WhitespaceDiffEntry:
    key: str
    source_value: str
    target_value: str

    @property
    def source_leading(self) -> int:
        return len(self.source_value) - len(self.source_value.lstrip())

    @property
    def target_leading(self) -> int:
        return len(self.target_value) - len(self.target_value.lstrip())

    @property
    def source_trailing(self) -> int:
        return len(self.source_value) - len(self.source_value.rstrip())

    @property
    def target_trailing(self) -> int:
        return len(self.target_value) - len(self.target_value.rstrip())

    def __str__(self) -> str:
        return (
            f"{self.key}: leading {self.source_leading}->{self.target_leading}, "
            f"trailing {self.source_trailing}->{self.target_trailing}"
        )


@dataclass
class WhitespaceDiffResult:
    changed: List[WhitespaceDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changed or self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts: List[str] = []
        if self.changed:
            parts.append(f"{len(self.changed)} key(s) with whitespace differences")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} only in source")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} only in target")
        return "; ".join(parts) if parts else "no whitespace differences"


def _has_whitespace_diff(a: str, b: str) -> bool:
    """Return True when the two values differ only in surrounding whitespace pattern."""
    return (a != b) and (
        a.lstrip() != a
        or a.rstrip() != a
        or b.lstrip() != b
        or b.rstrip() != b
        or a.strip() == b.strip()
    )


def diff_whitespace(
    source: Dict[str, str],
    target: Dict[str, str],
) -> WhitespaceDiffResult:
    result = WhitespaceDiffResult()
    source_keys = set(source)
    target_keys = set(target)

    result.only_in_source = sorted(source_keys - target_keys)
    result.only_in_target = sorted(target_keys - source_keys)

    for key in sorted(source_keys & target_keys):
        sv, tv = source[key], target[key]
        if sv != tv and (
            sv.lstrip() != sv or sv.rstrip() != sv
            or tv.lstrip() != tv or tv.rstrip() != tv
        ):
            result.changed.append(WhitespaceDiffEntry(key=key, source_value=sv, target_value=tv))

    return result
