"""Compare structural properties of two .env files (key count, empty values, etc.)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StructureDiffResult:
    source_key_count: int
    target_key_count: int
    source_empty_keys: List[str]
    target_empty_keys: List[str]
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)
    type_changes: Dict[str, tuple] = field(default_factory=dict)  # key -> (src_type, tgt_type)

    def has_differences(self) -> bool:
        return (
            self.source_key_count != self.target_key_count
            or bool(self.only_in_source)
            or bool(self.only_in_target)
            or self.source_empty_keys != self.target_empty_keys
            or bool(self.type_changes)
        )

    def summary(self) -> str:
        parts: List[str] = []
        parts.append(f"source keys: {self.source_key_count}, target keys: {self.target_key_count}")
        if self.only_in_source:
            parts.append(f"only in source: {', '.join(self.only_in_source)}")
        if self.only_in_target:
            parts.append(f"only in target: {', '.join(self.only_in_target)}")
        if self.source_empty_keys:
            parts.append(f"empty in source: {', '.join(self.source_empty_keys)}")
        if self.target_empty_keys:
            parts.append(f"empty in target: {', '.join(self.target_empty_keys)}")
        if self.type_changes:
            changes = ", ".join(f"{k}: {v[0]}->{v[1]}" for k, v in self.type_changes.items())
            parts.append(f"type changes: {changes}")
        return "; ".join(parts) if parts else "no structural differences"


def _infer_type(value: str) -> str:
    """Infer a loose type label for a value string."""
    if value == "":
        return "empty"
    if value.lower() in {"true", "false"}:
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


def diff_structure(
    source: Dict[str, str],
    target: Dict[str, str],
) -> StructureDiffResult:
    """Return a StructureDiffResult comparing two env dicts."""
    src_keys = set(source)
    tgt_keys = set(target)

    only_in_source = sorted(src_keys - tgt_keys)
    only_in_target = sorted(tgt_keys - src_keys)
    source_empty = sorted(k for k, v in source.items() if v == "")
    target_empty = sorted(k for k, v in target.items() if v == "")

    type_changes: Dict[str, tuple] = {}
    for key in src_keys & tgt_keys:
        src_type = _infer_type(source[key])
        tgt_type = _infer_type(target[key])
        if src_type != tgt_type:
            type_changes[key] = (src_type, tgt_type)

    return StructureDiffResult(
        source_key_count=len(source),
        target_key_count=len(target),
        source_empty_keys=source_empty,
        target_empty_keys=target_empty,
        only_in_source=only_in_source,
        only_in_target=only_in_target,
        type_changes=type_changes,
    )
