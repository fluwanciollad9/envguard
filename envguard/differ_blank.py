"""Diff blank/empty-value keys between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class BlankDiffResult:
    """Result of comparing blank keys across two environments."""

    source_blanks: Set[str] = field(default_factory=set)
    target_blanks: Set[str] = field(default_factory=set)

    # Keys blank in source but not in target (fixed in target)
    fixed: List[str] = field(default_factory=list)
    # Keys blank in target but not in source (regressed in target)
    regressed: List[str] = field(default_factory=list)
    # Keys blank in both
    still_blank: List[str] = field(default_factory=list)

    def has_regressions(self) -> bool:
        """Return True if target introduced new blank values."""
        return len(self.regressed) > 0

    def has_differences(self) -> bool:
        """Return True if blank-key sets differ at all."""
        return bool(self.fixed or self.regressed)

    def summary(self) -> str:
        parts: List[str] = []
        if self.still_blank:
            parts.append(f"{len(self.still_blank)} still blank")
        if self.fixed:
            parts.append(f"{len(self.fixed)} fixed")
        if self.regressed:
            parts.append(f"{len(self.regressed)} regressed")
        if not parts:
            return "No blank-value differences."
        return "Blank diff: " + ", ".join(parts) + "."


def diff_blank(
    source: Dict[str, str],
    target: Dict[str, str],
) -> BlankDiffResult:
    """Compare which keys have blank values in *source* vs *target*.

    A value is considered blank when it is an empty string or contains
    only whitespace characters.
    """
    src_blanks: Set[str] = {k for k, v in source.items() if not v.strip()}
    tgt_blanks: Set[str] = {k for k, v in target.items() if not v.strip()}

    fixed = sorted(src_blanks - tgt_blanks)
    regressed = sorted(tgt_blanks - src_blanks)
    still_blank = sorted(src_blanks & tgt_blanks)

    return BlankDiffResult(
        source_blanks=src_blanks,
        target_blanks=tgt_blanks,
        fixed=fixed,
        regressed=regressed,
        still_blank=still_blank,
    )
