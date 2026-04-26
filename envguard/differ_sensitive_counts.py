"""Counts-based diff for sensitive vs non-sensitive keys across two env files.

Provides a breakdown of how many sensitive and non-sensitive keys exist in
each environment, and highlights shifts that might indicate a security
regression (e.g. a secret key becoming a plain key, or a new sensitive key
being added without a counterpart).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Set

# Patterns that indicate a key holds sensitive data.
_SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"password",
        r"passwd",
        r"secret",
        r"token",
        r"api[_\-]?key",
        r"auth",
        r"private[_\-]?key",
        r"access[_\-]?key",
        r"credentials?",
        r"passphrase",
    ]
]


def _is_sensitive(key: str) -> bool:
    """Return True if *key* matches any known sensitive pattern."""
    return any(p.search(key) for p in _SENSITIVE_PATTERNS)


def _classify(env: Dict[str, str]) -> tuple[Set[str], Set[str]]:
    """Split *env* keys into (sensitive_keys, plain_keys)."""
    sensitive: Set[str] = set()
    plain: Set[str] = set()
    for key in env:
        (sensitive if _is_sensitive(key) else plain).add(key)
    return sensitive, plain


@dataclass
class SensitiveCountDiff:
    """Comparison of sensitive/plain key counts between two environments."""

    # Raw counts per environment
    source_sensitive: int
    source_plain: int
    target_sensitive: int
    target_plain: int

    # Keys that changed sensitivity classification between source and target
    became_sensitive: Set[str] = field(default_factory=set)
    became_plain: Set[str] = field(default_factory=set)

    # Keys that are new (only in target) and are sensitive
    new_sensitive: Set[str] = field(default_factory=set)
    # Keys that were removed from source and were sensitive
    removed_sensitive: Set[str] = field(default_factory=set)

    @property
    def sensitive_delta(self) -> int:
        """Net change in number of sensitive keys (target minus source)."""
        return self.target_sensitive - self.source_sensitive

    @property
    def has_regressions(self) -> bool:
        """True if any key moved from sensitive to plain (potential exposure)."""
        return bool(self.became_plain)

    @property
    def has_differences(self) -> bool:
        """True if any count or classification difference exists."""
        return (
            self.source_sensitive != self.target_sensitive
            or self.source_plain != self.target_plain
            or bool(self.became_sensitive)
            or bool(self.became_plain)
            or bool(self.new_sensitive)
            or bool(self.removed_sensitive)
        )

    def summary(self) -> str:
        """Return a human-readable one-line summary of the diff."""
        parts: list[str] = []
        if self.sensitive_delta > 0:
            parts.append(f"+{self.sensitive_delta} sensitive key(s)")
        elif self.sensitive_delta < 0:
            parts.append(f"{self.sensitive_delta} sensitive key(s)")
        if self.became_plain:
            parts.append(f"{len(self.became_plain)} key(s) lost sensitive classification")
        if self.became_sensitive:
            parts.append(f"{len(self.became_sensitive)} key(s) gained sensitive classification")
        if self.new_sensitive:
            parts.append(f"{len(self.new_sensitive)} new sensitive key(s) in target")
        if self.removed_sensitive:
            parts.append(f"{len(self.removed_sensitive)} sensitive key(s) removed")
        return "; ".join(parts) if parts else "no sensitive-key count differences"


def diff_sensitive_counts(
    source: Dict[str, str],
    target: Dict[str, str],
) -> SensitiveCountDiff:
    """Compare sensitive/plain key distributions between *source* and *target*.

    Args:
        source: Parsed key/value mapping for the baseline environment.
        target: Parsed key/value mapping for the environment being compared.

    Returns:
        A :class:`SensitiveCountDiff` describing all count-level and
        classification-level differences.
    """
    src_sensitive, src_plain = _classify(source)
    tgt_sensitive, tgt_plain = _classify(target)

    common_keys = set(source) & set(target)

    # Keys that existed in both but switched classification
    became_sensitive = {k for k in common_keys if k in src_plain and k in tgt_sensitive}
    became_plain = {k for k in common_keys if k in src_sensitive and k in tgt_plain}

    # Keys only in target that are sensitive
    only_in_target = set(target) - set(source)
    new_sensitive = {k for k in only_in_target if _is_sensitive(k)}

    # Keys only in source that were sensitive
    only_in_source = set(source) - set(target)
    removed_sensitive = {k for k in only_in_source if _is_sensitive(k)}

    return SensitiveCountDiff(
        source_sensitive=len(src_sensitive),
        source_plain=len(src_plain),
        target_sensitive=len(tgt_sensitive),
        target_plain=len(tgt_plain),
        became_sensitive=became_sensitive,
        became_plain=became_plain,
        new_sensitive=new_sensitive,
        removed_sensitive=removed_sensitive,
    )
