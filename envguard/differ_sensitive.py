"""Diff two env dicts, highlighting changes to sensitive keys separately."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_PATTERNS = ("password", "secret", "token", "api_key", "apikey", "private")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


@dataclass
class SensitiveDiffEntry:
    key: str
    old_value: str | None
    new_value: str | None
    is_sensitive: bool

    @property
    def is_added(self) -> bool:
        return self.old_value is None and self.new_value is not None

    @property
    def is_removed(self) -> bool:
        return self.old_value is not None and self.new_value is None

    @property
    def is_modified(self) -> bool:
        return self.old_value is not None and self.new_value is not None and self.old_value != self.new_value


@dataclass
class SensitiveDiffResult:
    changes: List[SensitiveDiffEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def sensitive_changes(self) -> List[SensitiveDiffEntry]:
        return [c for c in self.changes if c.is_sensitive]

    @property
    def non_sensitive_changes(self) -> List[SensitiveDiffEntry]:
        return [c for c in self.changes if not c.is_sensitive]

    def summary(self) -> str:
        total = len(self.changes)
        sensitive = len(self.sensitive_changes)
        if total == 0:
            return "No differences found."
        return (
            f"{total} change(s) detected: "
            f"{sensitive} sensitive, {total - sensitive} non-sensitive."
        )


def diff_sensitive(
    source: Dict[str, str],
    target: Dict[str, str],
) -> SensitiveDiffResult:
    """Compare source and target env dicts; tag each change as sensitive or not."""
    changes: List[SensitiveDiffEntry] = []
    all_keys = set(source) | set(target)
    for key in sorted(all_keys):
        old = source.get(key)
        new = target.get(key)
        if old != new:
            changes.append(
                SensitiveDiffEntry(
                    key=key,
                    old_value=old,
                    new_value=new,
                    is_sensitive=_is_sensitive(key),
                )
            )
    return SensitiveDiffResult(changes=changes)
