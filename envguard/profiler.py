"""Profile an .env file: count keys, detect empty values, estimate entropy."""
from __future__ import annotations
import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProfileResult:
    total_keys: int
    empty_keys: List[str]
    long_values: List[str]  # keys whose value exceeds threshold
    avg_value_length: float
    entropy_scores: Dict[str, float]  # per-key Shannon entropy

    def summary(self) -> str:
        lines = [
            f"Total keys     : {self.total_keys}",
            f"Empty keys     : {len(self.empty_keys)}",
            f"Long values    : {len(self.long_values)}",
            f"Avg value len  : {self.avg_value_length:.1f}",
        ]
        return "\n".join(lines)


def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    freq = {ch: value.count(ch) / len(value) for ch in set(value)}
    return -sum(p * math.log2(p) for p in freq.values())


def profile_env(
    env: Dict[str, str],
    long_value_threshold: int = 100,
) -> ProfileResult:
    empty_keys = [k for k, v in env.items() if v == ""]
    long_values = [k for k, v in env.items() if len(v) > long_value_threshold]
    lengths = [len(v) for v in env.values()]
    avg_len = statistics.mean(lengths) if lengths else 0.0
    entropy_scores = {k: _shannon_entropy(v) for k, v in env.items()}
    return ProfileResult(
        total_keys=len(env),
        empty_keys=empty_keys,
        long_values=long_values,
        avg_value_length=avg_len,
        entropy_scores=entropy_scores,
    )
