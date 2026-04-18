"""Type-checking for .env values against a schema."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import re

_TYPE_PATTERNS: Dict[str, re.Pattern] = {
    "int": re.compile(r"^-?\d+$"),
    "float": re.compile(r"^-?\d+(\.\d+)?$"),
    "bool": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    "url": re.compile(r"^https?://.+"),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
}


@dataclass
class TypeIssue:
    key: str
    expected: str
    actual_value: str

    def __str__(self) -> str:
        return f"{self.key}: expected type '{self.expected}', got value '{self.actual_value}'"


@dataclass
class TypeCheckResult:
    issues: List[TypeIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)

    def summary(self) -> str:
        if not self.issues:
            return "All values match expected types."
        lines = [f"{len(self.issues)} type issue(s) found:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def typecheck_env(
    env: Dict[str, str],
    type_map: Dict[str, str],
) -> TypeCheckResult:
    """Validate env values against expected types defined in type_map.

    type_map: {KEY: type_name}, where type_name is one of int, float, bool, url, email.
    """
    issues: List[TypeIssue] = []
    for key, expected_type in type_map.items():
        if key not in env:
            continue
        value = env[key]
        pattern = _TYPE_PATTERNS.get(expected_type)
        if pattern is None:
            raise ValueError(f"Unknown type '{expected_type}' for key '{key}'")
        if not pattern.match(value):
            issues.append(TypeIssue(key=key, expected=expected_type, actual_value=value))
    return TypeCheckResult(issues=issues)
