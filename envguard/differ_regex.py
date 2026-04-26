"""Diff two .env files by matching keys against a regex pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RegexDiffEntry:
    key: str
    source_value: Optional[str]
    target_value: Optional[str]

    def is_added(self) -> bool:
        return self.source_value is None and self.target_value is not None

    def is_removed(self) -> bool:
        return self.source_value is not None and self.target_value is None

    def is_modified(self) -> bool:
        return (
            self.source_value is not None
            and self.target_value is not None
            and self.source_value != self.target_value
        )

    def __str__(self) -> str:
        if self.is_added():
            return f"+{self.key}={self.target_value}"
        if self.is_removed():
            return f"-{self.key}={self.source_value}"
        return f"~{self.key}: {self.source_value!r} -> {self.target_value!r}"


@dataclass
class RegexDiffResult:
    pattern: str
    matched_keys: List[str] = field(default_factory=list)
    changes: List[RegexDiffEntry] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changes)

    def summary(self) -> str:
        if not self.changes:
            return f"No differences in keys matching /{self.pattern}/"
        added = sum(1 for c in self.changes if c.is_added())
        removed = sum(1 for c in self.changes if c.is_removed())
        modified = sum(1 for c in self.changes if c.is_modified())
        parts = []
        if added:
            parts.append(f"{added} added")
        if removed:
            parts.append(f"{removed} removed")
        if modified:
            parts.append(f"{modified} modified")
        return f"Pattern /{self.pattern}/: {', '.join(parts)} (of {len(self.matched_keys)} matched keys)"


def diff_env_by_regex(
    source: Dict[str, str],
    target: Dict[str, str],
    pattern: str,
) -> RegexDiffResult:
    """Return differences for keys whose names match *pattern* (regex)."""
    rx = re.compile(pattern)
    all_keys = sorted(set(source) | set(target))
    matched = [k for k in all_keys if rx.search(k)]

    changes: List[RegexDiffEntry] = []
    for key in matched:
        src_val = source.get(key)
        tgt_val = target.get(key)
        if src_val != tgt_val:
            changes.append(RegexDiffEntry(key=key, source_value=src_val, target_value=tgt_val))

    return RegexDiffResult(pattern=pattern, matched_keys=matched, changes=changes)
