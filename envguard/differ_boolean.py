"""Diff boolean-typed values between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def _is_bool(value: str) -> bool:
    return value.strip().lower() in _BOOL_TRUE | _BOOL_FALSE


def _to_bool(value: str) -> Optional[bool]:
    v = value.strip().lower()
    if v in _BOOL_TRUE:
        return True
    if v in _BOOL_FALSE:
        return False
    return None


@dataclass
class BoolDiffEntry:
    key: str
    source_value: str
    target_value: str
    source_bool: Optional[bool]
    target_bool: Optional[bool]

    def is_semantic_change(self) -> bool:
        """True when parsed boolean meaning differs between source and target."""
        return self.source_bool != self.target_bool

    def __str__(self) -> str:
        return (
            f"{self.key}: {self.source_value!r} ({self.source_bool})"
            f" -> {self.target_value!r} ({self.target_bool})"
        )


@dataclass
class BoolDiffResult:
    changed: List[BoolDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)
    non_bool_keys: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changed or self.only_in_source or self.only_in_target)

    def semantic_changes(self) -> List[BoolDiffEntry]:
        return [e for e in self.changed if e.is_semantic_change()]

    def summary(self) -> str:
        parts = []
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} only in source")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} only in target")
        if self.non_bool_keys:
            parts.append(f"{len(self.non_bool_keys)} non-boolean skipped")
        return ", ".join(parts) if parts else "no boolean differences"


def diff_boolean(
    source: Dict[str, str],
    target: Dict[str, str],
) -> BoolDiffResult:
    """Compare boolean-valued keys across two env mappings."""
    result = BoolDiffResult()
    source_bool = {k: v for k, v in source.items() if _is_bool(v)}
    target_bool = {k: v for k, v in target.items() if _is_bool(v)}

    non_bool_in_source = {k for k in source if not _is_bool(source[k])}
    non_bool_in_target = {k for k in target if not _is_bool(target[k])}
    result.non_bool_keys = sorted(
        non_bool_in_source | non_bool_in_target
        - (set(source_bool) | set(target_bool))
    )

    all_bool_keys = set(source_bool) | set(target_bool)
    for key in sorted(all_bool_keys):
        in_src = key in source_bool
        in_tgt = key in target_bool
        if in_src and not in_tgt:
            result.only_in_source.append(key)
        elif in_tgt and not in_src:
            result.only_in_target.append(key)
        else:
            sv, tv = source_bool[key], target_bool[key]
            if sv != tv:
                result.changed.append(
                    BoolDiffEntry(
                        key=key,
                        source_value=sv,
                        target_value=tv,
                        source_bool=_to_bool(sv),
                        target_bool=_to_bool(tv),
                    )
                )
    return result
