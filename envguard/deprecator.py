"""Detect deprecated keys in .env files based on a deprecation list."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationIssue:
    key: str
    message: str
    replacement: Optional[str] = None

    def __str__(self) -> str:
        base = f"{self.key}: {self.message}"
        if self.replacement:
            base += f" (use '{self.replacement}' instead)"
        return base


@dataclass
class DeprecateResult:
    issues: List[DeprecationIssue] = field(default_factory=list)
    checked: int = 0

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def summary(self) -> str:
        if not self.issues:
            return f"No deprecated keys found ({self.checked} checked)."
        lines = [f"{len(self.issues)} deprecated key(s) found:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


def check_deprecations(
    env: Dict[str, str],
    deprecations: Dict[str, Dict[str, str]],
) -> DeprecateResult:
    """Check env keys against a deprecation map.

    deprecations format:
        { "OLD_KEY": {"message": "...", "replacement": "NEW_KEY"} }
    The 'replacement' field is optional.
    """
    issues: List[DeprecationIssue] = []
    for key in env:
        if key in deprecations:
            entry = deprecations[key]
            issues.append(
                DeprecationIssue(
                    key=key,
                    message=entry.get("message", "This key is deprecated."),
                    replacement=entry.get("replacement"),
                )
            )
    return DeprecateResult(issues=issues, checked=len(env))
