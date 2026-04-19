from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class FilterResult:
    matched: Dict[str, str]
    excluded: Dict[str, str]
    pattern: str

    def match_count(self) -> int:
        return len(self.matched)

    def summary(self) -> str:
        return (
            f"{self.match_count()} key(s) matched pattern '{self.pattern}', "
            f"{len(self.excluded)} excluded."
        )


def filter_env(
    env: Dict[str, str],
    pattern: str,
    invert: bool = False,
    key_only: bool = True,
) -> FilterResult:
    """Filter env keys by regex pattern.

    Args:
        env: Parsed environment dict.
        pattern: Regular expression to match against.
        invert: If True, return keys that do NOT match.
        key_only: If True, match only against keys; otherwise match key OR value.
    """
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern '{pattern}': {exc}") from exc

    matched: Dict[str, str] = {}
    excluded: Dict[str, str] = {}

    for key, value in env.items():
        subject = key if key_only else f"{key}={value}"
        hits = bool(rx.search(subject))
        if invert:
            hits = not hits
        if hits:
            matched[key] = value
        else:
            excluded[key] = value

    return FilterResult(matched=matched, excluded=excluded, pattern=pattern)
