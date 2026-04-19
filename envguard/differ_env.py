"""Compare two .env files and report added, removed, and modified keys with values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EnvDiff:
    source_file: str
    target_file: str
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    modified: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Dict[str, str] = field(default_factory=dict)

    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.modified:
            parts.append(f"{len(self.modified)} modified")
        if not parts:
            return "No differences found."
        return "Differences: " + ", ".join(parts) + "."


def diff_env_files(source: Dict[str, str], target: Dict[str, str],
                   source_file: str = "source", target_file: str = "target") -> EnvDiff:
    result = EnvDiff(source_file=source_file, target_file=target_file)
    all_keys = set(source) | set(target)
    for key in all_keys:
        in_src = key in source
        in_tgt = key in target
        if in_src and not in_tgt:
            result.removed[key] = source[key]
        elif in_tgt and not in_src:
            result.added[key] = target[key]
        elif source[key] != target[key]:
            result.modified[key] = (source[key], target[key])
        else:
            result.unchanged[key] = source[key]
    return result
