"""Compare inferred types of values between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


def _infer_type(value: str) -> str:
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
    if value.startswith(("http://", "https://")):
        return "url"
    return "str"


@dataclass
class TypeDiffEntry:
    key: str
    source_type: str
    target_type: str

    def __str__(self) -> str:
        return f"{self.key}: {self.source_type} -> {self.target_type}"


@dataclass
class TypeDiffResult:
    source_label: str
    target_label: str
    changed: List[TypeDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changed or self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts: List[str] = []
        if self.changed:
            parts.append(f"{len(self.changed)} type change(s)")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} only in {self.source_label}")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} only in {self.target_label}")
        return ", ".join(parts) if parts else "no type differences"


def diff_types(
    source: Dict[str, str],
    target: Dict[str, str],
    source_label: str = "source",
    target_label: str = "target",
) -> TypeDiffResult:
    result = TypeDiffResult(source_label=source_label, target_label=target_label)
    all_keys = set(source) | set(target)
    for key in sorted(all_keys):
        in_src = key in source
        in_tgt = key in target
        if in_src and not in_tgt:
            result.only_in_source.append(key)
        elif in_tgt and not in_src:
            result.only_in_target.append(key)
        else:
            src_type = _infer_type(source[key])
            tgt_type = _infer_type(target[key])
            if src_type != tgt_type:
                result.changed.append(TypeDiffEntry(key=key, source_type=src_type, target_type=tgt_type))
    return result
