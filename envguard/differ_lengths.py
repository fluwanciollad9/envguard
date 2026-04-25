"""Compare value lengths between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class LengthDiffEntry:
    key: str
    source_len: int
    target_len: int

    @property
    def delta(self) -> int:
        return self.target_len - self.source_len

    @property
    def is_longer(self) -> bool:
        return self.delta > 0

    @property
    def is_shorter(self) -> bool:
        return self.delta < 0

    def __str__(self) -> str:
        direction = "+" if self.delta >= 0 else ""
        return f"{self.key}: {self.source_len} -> {self.target_len} ({direction}{self.delta})"


@dataclass
class LengthDiffResult:
    source_file: str
    target_file: str
    changed: List[LengthDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changed or self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts: List[str] = []
        if self.changed:
            parts.append(f"{len(self.changed)} length change(s)")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} key(s) only in source")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} key(s) only in target")
        return "; ".join(parts) if parts else "no differences"

    def longer_in_target(self) -> List[LengthDiffEntry]:
        return [e for e in self.changed if e.is_longer]

    def shorter_in_target(self) -> List[LengthDiffEntry]:
        return [e for e in self.changed if e.is_shorter]


def diff_lengths(
    source: Dict[str, str],
    target: Dict[str, str],
    source_file: str = "source",
    target_file: str = "target",
) -> LengthDiffResult:
    result = LengthDiffResult(source_file=source_file, target_file=target_file)
    source_keys = set(source)
    target_keys = set(target)

    result.only_in_source = sorted(source_keys - target_keys)
    result.only_in_target = sorted(target_keys - source_keys)

    for key in sorted(source_keys & target_keys):
        sl = len(source[key])
        tl = len(target[key])
        if sl != tl:
            result.changed.append(LengthDiffEntry(key=key, source_len=sl, target_len=tl))

    return result
