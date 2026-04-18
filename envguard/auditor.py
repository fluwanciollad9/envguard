"""Audit .env files for common security and quality issues."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_WEAK_PATTERNS = [
    re.compile(r'^(password|secret|token|key|api_key|apikey)$', re.IGNORECASE),
]

_PLACEHOLDER_VALUES = {"changeme", "todo", "fixme", "example", "placeholder", "xxx", "your_secret_here"}

_SHORT_SECRET_THRESHOLD = 8


@dataclass
class AuditIssue:
    key: str
    message: str
    severity: str  # "warning" | "error"


@dataclass
class AuditResult:
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def _looks_like_secret_key(key: str) -> bool:
    return any(p.search(key) for p in _WEAK_PATTERNS)


def audit_env(env: Dict[str, str]) -> AuditResult:
    """Run security and quality checks on a parsed env dict."""
    result = AuditResult()

    for key, value in env.items():
        stripped = value.strip()

        # Empty values for secret-looking keys
        if _looks_like_secret_key(key) and not stripped:
            result.issues.append(AuditIssue(key=key, message="Secret key has empty value", severity="error"))
            continue

        # Placeholder values
        if stripped.lower() in _PLACEHOLDER_VALUES:
            result.issues.append(AuditIssue(key=key, message=f"Value looks like a placeholder: {stripped!r}", severity="warning"))

        # Short secrets
        if _looks_like_secret_key(key) and stripped and len(stripped) < _SHORT_SECRET_THRESHOLD:
            result.issues.append(AuditIssue(key=key, message=f"Secret value is suspiciously short ({len(stripped)} chars)", severity="warning"))

        # Unquoted whitespace
        if value != stripped and not (value.startswith('"') or value.startswith("'")):
            result.issues.append(AuditIssue(key=key, message="Value has leading/trailing whitespace", severity="warning"))

    return result
