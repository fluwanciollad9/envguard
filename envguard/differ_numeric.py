"""Numeric diff: compare keys whose values are numeric across two env files.

For each key present in both envs where at least one value is numeric,
records the source value, target value, and the arithmetic delta.
Keys that are only in one file are tracked separately.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


def _to_number(value: str) -> Optional[float]:
    """Try to parse *value* as a float; return None if it cannot be parsed."""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None


@dataclass
class NumericDiffEntry:
    """A single key whose numeric value differs (or exists in only one env)."""

    key: str
    source_raw: Optional[str]  # None when key is only in target
    target_raw: Optional[str]  # None when key is only in source

    @property
    def source_number(self) -> Optional[float]:
        """Parsed numeric value from the source env, or None."""
        return _to_number(self.source_raw) if self.source_raw is not None else None

    @property
    def target_number(self) -> Optional[float]:
        """Parsed numeric value from the target env, or None."""
        return _to_number(self.target_raw) if self.target_raw is not None else None

    @property
    def delta(self) -> Optional[float]:
        """target - source when both are numeric, otherwise None."""
        s, t = self.source_number, self.target_number
        if s is not None and t is not None:
            return t - s
        return None

    def is_added(self) -> bool:
        """True when the key exists only in the target."""
        return self.source_raw is None

    def is_removed(self) -> bool:
        """True when the key exists only in the source."""
        return self.target_raw is None

    def is_increased(self) -> bool:
        """True when the numeric value grew from source to target."""
        d = self.delta
        return d is not None and d > 0

    def is_decreased(self) -> bool:
        """True when the numeric value shrank from source to target."""
        d = self.delta
        return d is not None and d < 0

    def __str__(self) -> str:  # noqa: D105
        if self.is_added():
            return f"{self.key}: [added] target={self.target_raw}"
        if self.is_removed():
            return f"{self.key}: [removed] source={self.source_raw}"
        arrow = "↑" if self.is_increased() else ("↓" if self.is_decreased() else "=")
        delta_str = f"{self.delta:+g}" if self.delta is not None else "n/a"
        return (
            f"{self.key}: {self.source_raw} → {self.target_raw} "
            f"({arrow} {delta_str})"
        )


@dataclass
class NumericDiffResult:
    """Aggregated result of a numeric diff between two env mappings."""

    changed: List[NumericDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)
    # Keys present in both envs but neither value is numeric
    non_numeric_skipped: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        """Return True if any numeric values changed or keys were added/removed."""
        return bool(self.changed or self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        """Human-readable one-line summary."""
        parts: List[str] = []
        if self.changed:
            increased = sum(1 for e in self.changed if e.is_increased())
            decreased = sum(1 for e in self.changed if e.is_decreased())
            parts.append(
                f"{len(self.changed)} changed "
                f"({increased} increased, {decreased} decreased)"
            )
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} only in source")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} only in target")
        if not parts:
            return "No numeric differences."
        return "; ".join(parts) + "."


def diff_numeric(
    source: Dict[str, str],
    target: Dict[str, str],
) -> NumericDiffResult:
    """Compare numeric values between *source* and *target* env mappings.

    Parameters
    ----------
    source:
        Mapping parsed from the baseline .env file.
    target:
        Mapping parsed from the comparison .env file.

    Returns
    -------
    NumericDiffResult
        Populated with changed entries and keys that appear in only one env.
    """
    result = NumericDiffResult()

    all_keys = set(source) | set(target)

    for key in sorted(all_keys):
        in_source = key in source
        in_target = key in target

        if in_source and not in_target:
            # Only track if the source value is numeric
            if _to_number(source[key]) is not None:
                result.only_in_source.append(key)
            continue

        if in_target and not in_source:
            if _to_number(target[key]) is not None:
                result.only_in_target.append(key)
            continue

        # Present in both
        src_num = _to_number(source[key])
        tgt_num = _to_number(target[key])

        if src_num is None and tgt_num is None:
            result.non_numeric_skipped.append(key)
            continue

        # At least one is numeric — record if values differ
        if source[key].strip() != target[key].strip():
            result.changed.append(
                NumericDiffEntry(
                    key=key,
                    source_raw=source[key],
                    target_raw=target[key],
                )
            )

    return result
