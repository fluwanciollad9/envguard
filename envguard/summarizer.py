"""Summarizer: produce a high-level summary report of a .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.profiler import profile_env
from envguard.placeholder import find_placeholders
from envguard.auditor import audit_env
from envguard.scorer import score_env


@dataclass
class SummaryReport:
    total_keys: int
    empty_keys: List[str]
    placeholder_keys: List[str]
    audit_errors: int
    audit_warnings: int
    score: float
    grade: str
    entropy_by_key: Dict[str, float] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Total keys      : {self.total_keys}",
            f"Empty keys      : {len(self.empty_keys)}",
            f"Placeholders    : {len(self.placeholder_keys)}",
            f"Audit errors    : {self.audit_errors}",
            f"Audit warnings  : {self.audit_warnings}",
            f"Score           : {self.score:.1f} / 100  [{self.grade}]",
        ]
        return "\n".join(lines)


def summarize_env(env: Dict[str, str], passphrase: str = "") -> SummaryReport:
    """Run all analysis passes and return a consolidated SummaryReport."""
    profile = profile_env(env)
    placeholders = find_placeholders(env)
    audit = audit_env(env, passphrase=passphrase)
    score_result = score_env(env)

    return SummaryReport(
        total_keys=profile.total_keys,
        empty_keys=profile.empty_keys,
        placeholder_keys=list(placeholders.found.keys()),
        audit_errors=len([i for i in audit.issues if i.severity == "error"]),
        audit_warnings=len([i for i in audit.issues if i.severity == "warning"]),
        score=score_result.score,
        grade=score_result.grade(),
        entropy_by_key=profile.entropy_by_key,
    )
