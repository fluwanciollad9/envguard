"""Promote env values from one environment to another, tracking what changed."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PromoteResult:
    source_env: str
    target_env: str
    promoted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    def was_changed(self) -> bool:
        return bool(self.promoted)

    def summary(self) -> str:
        parts = [f"Promoted {len(self.promoted)} key(s) from '{self.source_env}' to '{self.target_env}'."]
        if self.overwritten:
            parts.append(f"Overwritten: {', '.join(sorted(self.overwritten))}.")
        if self.skipped:
            parts.append(f"Skipped (already present): {', '.join(sorted(self.skipped))}.")
        return " ".join(parts)


def promote_env(
    source: Dict[str, str],
    target: Dict[str, str],
    keys: List[str],
    overwrite: bool = False,
    source_label: str = "source",
    target_label: str = "target",
) -> PromoteResult:
    result = PromoteResult(source_env=source_label, target_env=target_label)
    for key in keys:
        if key not in source:
            continue
        if key in target and not overwrite:
            result.skipped.append(key)
        else:
            if key in target:
                result.overwritten.append(key)
            result.promoted[key] = source[key]
    return result


def render_promoted(base: Dict[str, str], result: PromoteResult) -> str:
    merged = {**base, **result.promoted}
    lines = [f"{k}={v}" for k, v in merged.items()]
    return "\n".join(lines) + ("\n" if lines else "")
