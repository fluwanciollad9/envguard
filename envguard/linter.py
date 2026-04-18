"""Lint .env files for style and consistency issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import re


@dataclass
class LintIssue:
    line: int
    message: str
    severity: str  # "error" | "warning"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_VALID_LINE_RE = re.compile(r'^\s*(#.*)?$|^[A-Za-z_][A-Za-z0-9_]*\s*=')


def lint_env(path: str) -> LintResult:
    result = LintResult()
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        # Skip blanks and comments
        if not line.strip() or line.strip().startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(LintIssue(lineno, f"Line has no '=' separator: {line!r}", "error"))
            continue

        key, _, _ = line.partition("=")
        key = key.strip()

        if not key:
            result.issues.append(LintIssue(lineno, "Empty key before '='", "error"))
            continue

        if not _KEY_RE.match(key):
            result.issues.append(
                LintIssue(lineno, f"Key {key!r} should be UPPER_SNAKE_CASE", "warning")
            )

        if line != line.rstrip():
            result.issues.append(LintIssue(lineno, f"Trailing whitespace on line", "warning"))

    return result
