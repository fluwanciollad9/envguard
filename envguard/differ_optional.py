"""Diff optional (non-required) keys between two env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class OptionalDiffEntry:
    key: str
    source_value: str | None
    target_value: str | None

    @property
    def is_added(self) -> bool:
        return self.source_value is None and self.target_value is not None

    @property
    def is_removed(self) -> bool:
        return self.source_value is not None and self.target_value is None

    @property
    def is_modified(self) -> bool:
        return (
            self.source_value is not None
            and self.target_value is not None
            and self.source_value != self.target_value
        )

    def __str__(self) -> str:
        if self.is_added:
            return f"+{self.key}={self.target_value}"
        if self.is_removed:
            return f"-{self.key}={self.source_value}"
        return f"~{self.key}: {self.source_value!r} -> {self.target_value!r}"


@dataclass
class OptionalDiffResult:
    optional_keys: Set[str]
    changes: List[OptionalDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changes or self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts = []
        if self.changes:
            parts.append(f"{len(self.changes)} changed")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} removed")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} added")
        if not parts:
            return "no differences in optional keys"
        return "; ".join(parts)


def diff_optional(
    source: Dict[str, str],
    target: Dict[str, str],
    optional_keys: Set[str],
) -> OptionalDiffResult:
    """Compare only the optional keys between source and target envs."""
    src_optional = {k: v for k, v in source.items() if k in optional_keys}
    tgt_optional = {k: v for k, v in target.items() if k in optional_keys}

    all_keys = set(src_optional) | set(tgt_optional)
    changes: List[OptionalDiffEntry] = []
    only_in_source: List[str] = []
    only_in_target: List[str] = []

    for key in sorted(all_keys):
        in_src = key in src_optional
        in_tgt = key in tgt_optional
        if in_src and in_tgt:
            if src_optional[key] != tgt_optional[key]:
                changes.append(
                    OptionalDiffEntry(key, src_optional[key], tgt_optional[key])
                )
        elif in_src:
            only_in_source.append(key)
        else:
            only_in_target.append(key)

    return OptionalDiffResult(
        optional_keys=optional_keys,
        changes=changes,
        only_in_source=only_in_source,
        only_in_target=only_in_target,
    )
