"""Detect and trim trailing whitespace from .env values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TrimResult:
    original: Dict[str, str]
    trimmed: Dict[str, str]
    changed_keys: List[str] = field(default_factory=list)


def was_changed(result: TrimResult) -> bool:
    return len(result.changed_keys) > 0


def trim_env(env: Dict[str, str]) -> TrimResult:
    trimmed: Dict[str, str] = {}
    changed_keys: List[str] = []
    for key, value in env.items():
        clean = value.strip()
        trimmed[key] = clean
        if clean != value:
            changed_keys.append(key)
    return TrimResult(original=dict(env), trimmed=trimmed, changed_keys=changed_keys)


def render_trimmed(env: Dict[str, str]) -> str:
    lines: List[str] = []
    for key, value in env.items():
        if " " in value or value == "":
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
