from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        for prefix, keys in sorted(self.groups.items()):
            lines.append(f"[{prefix}] {len(keys)} key(s): {', '.join(keys)}")
        if self.ungrouped:
            lines.append(f"[ungrouped] {len(self.ungrouped)} key(s): {', '.join(self.ungrouped)}")
        return "\n".join(lines) if lines else "No keys found."

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())


def group_env(env: Dict[str, str], prefixes: List[str] | None = None) -> GroupResult:
    """Group env keys by common prefix (e.g. DB_, AWS_, APP_).

    If prefixes is None, prefixes are auto-detected from key names using
    the portion before the first underscore.
    """
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for key in sorted(env.keys()):
        matched = False
        if prefixes is not None:
            for prefix in prefixes:
                if key.upper().startswith(prefix.upper()):
                    bucket = prefix.upper()
                    groups.setdefault(bucket, [])
                    groups[bucket].append(key)
                    matched = True
                    break
        else:
            if "_" in key:
                bucket = key.split("_")[0].upper()
                groups.setdefault(bucket, [])
                groups[bucket].append(key)
                matched = True

        if not matched:
            ungrouped.append(key)

    return GroupResult(groups=groups, ungrouped=ungrouped)
