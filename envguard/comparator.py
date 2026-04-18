"""Compare two .env files and produce a structured value-level comparison."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValueChange:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]

    @property
    def is_added(self) -> bool:
        return self.old_value is None and self.new_value is not None

    @property
    def is_removed(self) -> bool:
        return self.old_value is not None and self.new_value is None

    @property
    def is_modified(self) -> bool:
        return self.old_value is not None and self.new_value is not None

    def __str__(self) -> str:
        if self.is_added:
            return f"+ {self.key}={self.new_value}"
        if self.is_removed:
            return f"- {self.key}={self.old_value}"
        return f"~ {self.key}: {self.old_value!r} -> {self.new_value!r}"


@dataclass
class CompareResult:
    changes: List[ValueChange] = field(default_factory=list)

    @property
    def added(self) -> List[ValueChange]:
        return [c for c in self.changes if c.is_added]

    @property
    def removed(self) -> List[ValueChange]:
        return [c for c in self.changes if c.is_removed]

    @property
    def modified(self) -> List[ValueChange]:
        return [c for c in self.changes if c.is_modified]

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    def summary(self) -> str:
        return (
            f"{len(self.added)} added, "
            f"{len(self.removed)} removed, "
            f"{len(self.modified)} modified"
        )


def compare_envs(base: Dict[str, str], target: Dict[str, str]) -> CompareResult:
    """Compare base env to target env, returning all value-level changes."""
    changes: List[ValueChange] = []
    all_keys = sorted(set(base) | set(target))
    for key in all_keys:
        if key not in base:
            changes.append(ValueChange(key, None, target[key]))
        elif key not in target:
            changes.append(ValueChange(key, base[key], None))
        elif base[key] != target[key]:
            changes.append(ValueChange(key, base[key], target[key]))
    return CompareResult(changes=changes)
