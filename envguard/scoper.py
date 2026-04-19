"""Scope filtering: extract env keys matching a given scope/prefix set."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    scope: str
    matched: Dict[str, str] = field(default_factory=dict)
    unmatched: Dict[str, str] = field(default_factory=dict)

    def match_count(self) -> int:
        return len(self.matched)

    def summary(self) -> str:
        total = len(self.matched) + len(self.unmatched)
        return (
            f"Scope '{self.scope}': {self.match_count()}/{total} keys matched."
        )


def scope_env(
    env: Dict[str, str],
    scope: str,
    strip_prefix: bool = False,
    case_sensitive: bool = False,
) -> ScopeResult:
    """Filter env keys by prefix scope.

    Args:
        env: Parsed environment dict.
        scope: Prefix to match (e.g. 'DB').
        strip_prefix: If True, remove the prefix from matched keys.
        case_sensitive: Whether prefix matching is case-sensitive.
    """
    prefix = scope if case_sensitive else scope.upper()
    prefix_with_sep = prefix + "_"

    matched: Dict[str, str] = {}
    unmatched: Dict[str, str] = {}

    for key, value in env.items():
        compare_key = key if case_sensitive else key.upper()
        if compare_key.startswith(prefix_with_sep) or compare_key == prefix:
            if strip_prefix and compare_key.startswith(prefix_with_sep):
                new_key = key[len(prefix_with_sep):]
            else:
                new_key = key
            matched[new_key] = value
        else:
            unmatched[key] = value

    return ScopeResult(scope=scope, matched=matched, unmatched=unmatched)
