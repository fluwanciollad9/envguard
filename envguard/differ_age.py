"""Compare .env files by the age/staleness of their values using a reference timestamp file."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AgeDiffEntry:
    key: str
    source_mtime: float
    target_mtime: float

    @property
    def delta_seconds(self) -> float:
        return self.target_mtime - self.source_mtime

    @property
    def is_newer(self) -> bool:
        return self.delta_seconds > 0

    @property
    def is_older(self) -> bool:
        return self.delta_seconds < 0

    def __str__(self) -> str:
        direction = "newer" if self.is_newer else "older"
        return f"{self.key}: target is {abs(self.delta_seconds):.1f}s {direction} than source"


@dataclass
class AgeDiffResult:
    source_file: str
    target_file: str
    changed: List[AgeDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changed or self.only_in_source or self.only_in_target)

    def summary(self) -> str:
        parts = []
        if self.changed:
            parts.append(f"{len(self.changed)} key(s) with differing timestamps")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} key(s) only in source")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} key(s) only in target")
        return "; ".join(parts) if parts else "no age differences"


def _load_timestamps(path: str) -> Dict[str, float]:
    """Load a JSON file mapping key -> unix timestamp."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Timestamp file not found: {path}")
    with p.open() as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Timestamp file must contain a JSON object: {path}")
    return {k: float(v) for k, v in data.items()}


def diff_age(
    source_ts_path: str,
    target_ts_path: str,
    threshold: float = 0.0,
) -> AgeDiffResult:
    """Diff two timestamp index files, flagging keys whose ages differ by more than threshold."""
    source_ts = _load_timestamps(source_ts_path)
    target_ts = _load_timestamps(target_ts_path)

    source_keys = set(source_ts)
    target_keys = set(target_ts)

    result = AgeDiffResult(source_file=source_ts_path, target_file=target_ts_path)
    result.only_in_source = sorted(source_keys - target_keys)
    result.only_in_target = sorted(target_keys - source_keys)

    for key in sorted(source_keys & target_keys):
        delta = abs(target_ts[key] - source_ts[key])
        if delta > threshold:
            result.changed.append(AgeDiffEntry(key, source_ts[key], target_ts[key]))

    return result
