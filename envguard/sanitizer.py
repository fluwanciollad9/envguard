"""Sanitize .env values by removing control characters and enforcing safe encoding."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import re

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass
class SanitizeIssue:
    key: str
    original: str
    sanitized: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.reason}"


@dataclass
class SanitizeResult:
    env: Dict[str, str]
    issues: List[SanitizeIssue] = field(default_factory=list)

    def was_changed(self) -> bool:
        return len(self.issues) > 0

    def summary(self) -> str:
        if not self.issues:
            return "No sanitization issues found."
        return f"{len(self.issues)} value(s) sanitized: " + ", ".join(i.key for i in self.issues)


def _sanitize_value(value: str) -> Tuple[str, str | None]:
    """Return (sanitized_value, reason) or (value, None) if clean."""
    stripped = value.strip()
    if stripped != value:
        return stripped, "leading/trailing whitespace removed"
    cleaned = _CONTROL_CHAR_RE.sub("", value)
    if cleaned != value:
        return cleaned, "control characters removed"
    return value, None


def sanitize_env(
    env: Dict[str, str],
    strip_whitespace: bool = True,
    remove_control_chars: bool = True,
) -> SanitizeResult:
    result_env: Dict[str, str] = {}
    issues: List[SanitizeIssue] = []

    for key, value in env.items():
        current = value
        reason_parts = []

        if strip_whitespace:
            stripped = current.strip()
            if stripped != current:
                reason_parts.append("leading/trailing whitespace removed")
                current = stripped

        if remove_control_chars:
            cleaned = _CONTROL_CHAR_RE.sub("", current)
            if cleaned != current:
                reason_parts.append("control characters removed")
                current = cleaned

        result_env[key] = current
        if reason_parts:
            issues.append(SanitizeIssue(
                key=key,
                original=value,
                sanitized=current,
                reason="; ".join(reason_parts),
            ))

    return SanitizeResult(env=result_env, issues=issues)
