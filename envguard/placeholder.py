"""Detect keys whose values look like unfilled placeholders."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import re

_PLACEHOLDER_PATTERNS = [
    re.compile(r'^<.+>$'),
    re.compile(r'^\{\{.+\}\}$'),
    re.compile(r'^\$\{.+\}$'),
    re.compile(r'^CHANGE[_-]?ME$', re.IGNORECASE),
    re.compile(r'^REPLACE[_-]?ME$', re.IGNORECASE),
    re.compile(r'^TODO$', re.IGNORECASE),
    re.compile(r'^FIXME$', re.IGNORECASE),
    re.compile(r'^YOUR[_-]', re.IGNORECASE),
    re.compile(r'^ENTER[_-]', re.IGNORECASE),
    re.compile(r'^\[.+\]$'),
]


def _is_placeholder(value: str) -> bool:
    return any(p.match(value.strip()) for p in _PLACEHOLDER_PATTERNS)


@dataclass
class PlaceholderResult:
    found: Dict[str, str] = field(default_factory=dict)

    @property
    def has_placeholders(self) -> bool:
        return bool(self.found)

    def summary(self) -> str:
        if not self.found:
            return "No placeholder values detected."
        lines = [f"  {k}={v}" for k, v in self.found.items()]
        return "Placeholder values detected:\n" + "\n".join(lines)


def find_placeholders(env: Dict[str, str]) -> PlaceholderResult:
    found = {k: v for k, v in env.items() if _is_placeholder(v)}
    return PlaceholderResult(found=found)
