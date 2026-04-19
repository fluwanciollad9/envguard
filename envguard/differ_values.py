"""Value-level diff between two env files, reporting changed, added, and removed keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValueDiff:
    """Represents a single key-level difference between two env mappings."""

    key: str
    source_value: Optional[str]  # None if key absent in source
    target_value: Optional[str]  # None if key absent in target

    @property
    def is_added(self) -> bool:
        """Key exists only in target."""
        return self.source_value is None and self.target_value is not None

    @property
    def is_removed(self) -> bool:
        """Key exists only in source."""
        return self.source_value is not None and self.target_value is None

    @property
    def is_modified(self) -> bool:
        """Key exists in both but values differ."""
        return (
            self.source_value is not None
            and self.target_value is not None
            and self.source_value != self.target_value
        )

    def __str__(self) -> str:
        if self.is_added:
            return f"+ {self.key}={self.target_value}"
        if self.is_removed:
            return f"- {self.key}={self.source_value}"
        return f"~ {self.key}: {self.source_value!r} -> {self.target_value!r}"


@dataclass
class ValueDiffResult:
    """Aggregated result of a value-level diff between two env mappings."""

    diffs: List[ValueDiff] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.diffs)

    @property
    def added(self) -> List[ValueDiff]:
        return [d for d in self.diffs if d.is_added]

    @property
    def removed(self) -> List[ValueDiff]:
        return [d for d in self.diffs if d.is_removed]

    @property
    def modified(self) -> List[ValueDiff]:
        return [d for d in self.diffs if d.is_modified]

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.modified:
            parts.append(f"{len(self.modified)} modified")
        return ", ".join(parts) if parts else "no differences"


def diff_values(
    source: Dict[str, str],
    target: Dict[str, str],
) -> ValueDiffResult:
    """Compare two env mappings and return a ValueDiffResult.

    Args:
        source: The baseline env mapping (e.g. .env.example).
        target: The env mapping to compare against (e.g. .env.production).

    Returns:
        A ValueDiffResult containing all detected differences.
    """
    diffs: List[ValueDiff] = []
    all_keys = sorted(set(source) | set(target))

    for key in all_keys:
        src_val = source.get(key)
        tgt_val = target.get(key)
        if src_val != tgt_val:
            diffs.append(ValueDiff(key=key, source_value=src_val, target_value=tgt_val))

    return ValueDiffResult(diffs=diffs)
