"""Key-set diff: find keys present in one env but absent in another."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class KeyDiffResult:
    source_name: str
    target_name: str
    only_in_source: Set[str] = field(default_factory=set)
    only_in_target: Set[str] = field(default_factory=set)
    common: Set[str] = field(default_factory=set)

    def has_differences(self) -> bool:
        return bool(self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts = []
        if self.only_in_source:
            keys = ", ".join(sorted(self.only_in_source))
            parts.append(f"Only in {self.source_name}: {keys}")
        if self.only_in_target:
            keys = ", ".join(sorted(self.only_in_target))
            parts.append(f"Only in {self.target_name}: {keys}")
        if not parts:
            return "No key differences."
        return " | ".join(parts)


def diff_keys(
    source: Dict[str, str],
    target: Dict[str, str],
    source_name: str = "source",
    target_name: str = "target",
) -> KeyDiffResult:
    src_keys = set(source.keys())
    tgt_keys = set(target.keys())
    return KeyDiffResult(
        source_name=source_name,
        target_name=target_name,
        only_in_source=src_keys - tgt_keys,
        only_in_target=tgt_keys - src_keys,
        common=src_keys & tgt_keys,
    )
