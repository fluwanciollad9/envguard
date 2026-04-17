"""Validate .env files against a schema of required and optional keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)
    empty_required: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not (self.missing_required or self.empty_required)

    def summary(self) -> str:
        lines = []
        if self.missing_required:
            lines.append("Missing required keys: " + ", ".join(sorted(self.missing_required)))
        if self.empty_required:
            lines.append("Empty required keys: " + ", ".join(sorted(self.empty_required)))
        if self.unknown_keys:
            lines.append("Unknown keys (not in schema): " + ", ".join(sorted(self.unknown_keys)))
        return "\n".join(lines) if lines else "All validations passed."


def validate_env(
    env: Dict[str, str],
    required: List[str],
    optional: Optional[List[str]] = None,
    allow_unknown: bool = True,
) -> ValidationResult:
    """Validate *env* dict against required/optional key schema."""
    result = ValidationResult()
    required_set: Set[str] = set(required)
    optional_set: Set[str] = set(optional or [])
    known: Set[str] = required_set | optional_set

    for key in required_set:
        if key not in env:
            result.missing_required.append(key)
        elif env[key] == "":
            result.empty_required.append(key)

    if not allow_unknown:
        for key in env:
            if key not in known:
                result.unknown_keys.append(key)

    return result
