"""Score an env file for overall health based on various checks."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ScoreResult:
    total: int
    breakdown: Dict[str, int] = field(default_factory=dict)
    penalties: Dict[str, int] = field(default_factory=dict)

    @property
    def grade(self) -> str:
        if self.total >= 90:
            return "A"
        if self.total >= 75:
            return "B"
        if self.total >= 60:
            return "C"
        if self.total >= 40:
            return "D"
        return "F"

    def summary(self) -> str:
        lines = [f"Score: {self.total}/100 (Grade: {self.grade})"]
        for reason, pts in self.penalties.items():
            lines.append(f"  -{pts}  {reason}")
        return "\n".join(lines)


def score_env(env: Dict[str, str], *, strict: bool = False) -> ScoreResult:
    score = 100
    penalties: Dict[str, int] = {}
    breakdown: Dict[str, int] = {}

    empty_keys = [k for k, v in env.items() if v == ""]
    if empty_keys:
        p = min(30, len(empty_keys) * 5)
        penalties[f"{len(empty_keys)} empty value(s)"] = p
        score -= p

    placeholder_markers = ("<", ">", "changeme", "todo", "fixme", "your_")
    ph_keys = [k for k, v in env.items() if any(m in v.lower() for m in placeholder_markers)]
    if ph_keys:
        p = min(20, len(ph_keys) * 5)
        penalties[f"{len(ph_keys)} placeholder value(s)"] = p
        score -= p

    sensitive_markers = ("password", "secret", "token", "api_key", "private")
    short_secrets = [
        k for k, v in env.items()
        if any(m in k.lower() for m in sensitive_markers) and 0 < len(v) < 8
    ]
    if short_secrets:
        p = min(20, len(short_secrets) * 5)
        penalties[f"{len(short_secrets)} short secret(s)"] = p
        score -= p

    lowercase_keys = [k for k in env if k != k.upper()]
    if lowercase_keys and strict:
        p = min(10, len(lowercase_keys) * 2)
        penalties[f"{len(lowercase_keys)} non-uppercase key(s)"] = p
        score -= p

    breakdown["empty"] = len(empty_keys)
    breakdown["placeholders"] = len(ph_keys)
    breakdown["short_secrets"] = len(short_secrets)
    breakdown["lowercase_keys"] = len(lowercase_keys)

    return ScoreResult(total=max(0, score), breakdown=breakdown, penalties=penalties)
