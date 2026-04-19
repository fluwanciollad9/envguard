"""Value-level diff between two .env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValueDiff:
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
            return f"+ {self.key}={self.target_value}"
        if self.is_removed():
            return f"- {self.key}={self.source_value}"
        return f"~ {self.key}: {self.source_value!r} -> {self.target_value!r}"


@dataclass
class ValueDiffResult:
    source_label: str
    target_label: str
    diffs: List[ValueDiff] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.diffs)

    def added(self) -> List[ValueDiff]:
        return [d for d in self.diffs if d.is_added()]

    def removed(self) -> List[ValueDiff]:
        return [d for d in self.diffs if d.is_removed()]

    def modified(self) -> List[ValueDiff]:
        return [d for d in self.diffs if d.is_modified()]

    def summary(self) -> str:
        a, r, m = len(self.added()), len(self.removed()), len(self.modified())
        return (
            f"{self.source_label} vs {self.target_label}: "
            f"+{a} added, -{r} removed, ~{m} modified, {len(self.unchanged)} unchanged"
        )


def diff_values(
    source: Dict[str, str],
    target: Dict[str, str],
    source_label: str = "source",
    target_label: str = "target",
) -> ValueDiffResult:
    all_keys = sorted(set(source) | set(target))
    diffs: List[ValueDiff] = []
    unchanged: List[str] = []

    for key in all_keys:
        sv = source.get(key)
        tv = target.get(key)
        if sv == tv:
            unchanged.append(key)
        else:
            diffs.append(ValueDiff(key=key, source_value=sv, target_value=tv))

    return ValueDiffResult(
        source_label=source_label,
        target_label=target_label,
        diffs=diffs,
        unchanged=unchanged,
    )
