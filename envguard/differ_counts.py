"""Count-based diff: compare key counts and value-length statistics across two envs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CountDiffResult:
    source_count: int
    target_count: int
    common_count: int
    only_in_source: int
    only_in_target: int
    source_avg_value_len: float
    target_avg_value_len: float
    longest_key_source: str
    longest_key_target: str
    key_count_delta: int = field(init=False)

    def __post_init__(self) -> None:
        self.key_count_delta = self.target_count - self.source_count

    def has_differences(self) -> bool:
        return self.key_count_delta != 0 or self.only_in_source > 0 or self.only_in_target > 0

    def summary(self) -> str:
        lines = [
            f"Source keys: {self.source_count}, Target keys: {self.target_count} (delta: {self.key_count_delta:+d})",
            f"Common: {self.common_count}, Only in source: {self.only_in_source}, Only in target: {self.only_in_target}",
            f"Avg value length — source: {self.source_avg_value_len:.1f}, target: {self.target_avg_value_len:.1f}",
            f"Longest key — source: '{self.longest_key_source}', target: '{self.longest_key_target}'",
        ]
        return "\n".join(lines)


def _avg_value_len(env: Dict[str, str]) -> float:
    if not env:
        return 0.0
    return sum(len(v) for v in env.values()) / len(env)


def _longest_key(env: Dict[str, str]) -> str:
    if not env:
        return ""
    return max(env.keys(), key=len)


def diff_counts(source: Dict[str, str], target: Dict[str, str]) -> CountDiffResult:
    """Produce a CountDiffResult comparing *source* and *target* envs."""
    src_keys = set(source)
    tgt_keys = set(target)
    common = src_keys & tgt_keys

    return CountDiffResult(
        source_count=len(source),
        target_count=len(target),
        common_count=len(common),
        only_in_source=len(src_keys - tgt_keys),
        only_in_target=len(tgt_keys - src_keys),
        source_avg_value_len=_avg_value_len(source),
        target_avg_value_len=_avg_value_len(target),
        longest_key_source=_longest_key(source),
        longest_key_target=_longest_key(target),
    )
