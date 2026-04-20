"""freezer.py – capture a frozen (read-only) snapshot of env vars and detect any mutations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class FreezeViolation:
    key: str
    original: str
    current: str

    def __str__(self) -> str:
        return f"{self.key}: expected {self.original!r}, got {self.current!r}"


@dataclass
class FreezeResult:
    frozen: Dict[str, str]
    violations: List[FreezeViolation] = field(default_factory=list)
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    def has_violations(self) -> bool:
        return bool(self.violations or self.new_keys or self.removed_keys)

    def summary(self) -> str:
        parts: List[str] = []
        if self.violations:
            parts.append(f"{len(self.violations)} value change(s)")
        if self.new_keys:
            parts.append(f"{len(self.new_keys)} new key(s)")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed key(s)")
        return ", ".join(parts) if parts else "no violations"


def freeze_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return an immutable copy of *env* to use as a freeze baseline."""
    return dict(env)


def check_freeze(
    frozen: Dict[str, str],
    current: Dict[str, str],
) -> FreezeResult:
    """Compare *current* against the *frozen* baseline and report any drift."""
    violations: List[FreezeViolation] = []
    new_keys: List[str] = []
    removed_keys: List[str] = []

    frozen_set = set(frozen)
    current_set = set(current)

    for key in frozen_set & current_set:
        if frozen[key] != current[key]:
            violations.append(FreezeViolation(key=key, original=frozen[key], current=current[key]))

    for key in current_set - frozen_set:
        new_keys.append(key)

    for key in frozen_set - current_set:
        removed_keys.append(key)

    return FreezeResult(
        frozen=frozen,
        violations=violations,
        new_keys=sorted(new_keys),
        removed_keys=sorted(removed_keys),
    )
