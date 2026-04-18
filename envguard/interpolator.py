"""Variable interpolation for .env files.

Supports ${VAR} and $VAR syntax, resolving references within the same env dict
or falling back to os.environ.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List

_BRACE_RE = re.compile(r"\$\{([^}]+)\}")
_BARE_RE = re.compile(r"\$([A-Z_][A-Z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str]
    unresolved_keys: List[str] = field(default_factory=list)

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved_keys)


def _resolve_value(value: str, env: Dict[str, str], allow_os: bool) -> tuple[str, bool]:
    """Return (resolved_value, all_refs_found)."""
    all_found = True

    def replace(match: re.Match) -> str:
        nonlocal all_found
        name = match.group(1)
        if name in env:
            return env[name]
        if allow_os and name in os.environ:
            return os.environ[name]
        all_found = False
        return match.group(0)

    result = _BRACE_RE.sub(replace, value)
    result = _BARE_RE.sub(replace, result)
    return result, all_found


def interpolate(env: Dict[str, str], allow_os: bool = True) -> InterpolationResult:
    """Interpolate all values in *env*, resolving cross-references.

    A single pass is performed; forward references are not supported.
    """
    resolved: Dict[str, str] = {}
    unresolved: List[str] = []

    for key, value in env.items():
        new_value, ok = _resolve_value(value, {**resolved, **env}, allow_os)
        resolved[key] = new_value
        if not ok:
            unresolved.append(key)

    return InterpolationResult(resolved=resolved, unresolved_keys=unresolved)
