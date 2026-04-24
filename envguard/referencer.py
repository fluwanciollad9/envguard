"""Find all variable references (${VAR} or $VAR) used across an env file."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

_BRACE_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_BARE_RE = re.compile(r"(?<!\$)\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class ReferenceResult:
    """Result of scanning an env dict for variable references."""

    # mapping of key -> list of keys it references
    references: Dict[str, List[str]] = field(default_factory=dict)
    # keys that are referenced but not defined in the env
    undefined: Set[str] = field(default_factory=set)
    # keys that are defined but never referenced by any other key
    unreferenced: Set[str] = field(default_factory=set)

    def has_undefined(self) -> bool:
        return bool(self.undefined)

    def summary(self) -> str:
        total = sum(len(v) for v in self.references.values())
        parts = [f"{total} reference(s) found across {len(self.references)} key(s)"]
        if self.undefined:
            parts.append(f"{len(self.undefined)} undefined: {', '.join(sorted(self.undefined))}")
        if self.unreferenced:
            parts.append(
                f"{len(self.unreferenced)} unreferenced: {', '.join(sorted(self.unreferenced))}"
            )
        return "; ".join(parts)


def _extract_refs(value: str) -> List[str]:
    """Return all variable names referenced in *value*."""
    brace = _BRACE_RE.findall(value)
    bare = _BARE_RE.findall(value)
    seen: list[str] = []
    for name in brace + bare:
        if name not in seen:
            seen.append(name)
    return seen


def find_references(env: Dict[str, str]) -> ReferenceResult:
    """Scan *env* and return a :class:`ReferenceResult`."""
    references: Dict[str, List[str]] = {}
    all_referenced: Set[str] = set()

    for key, value in env.items():
        refs = _extract_refs(value)
        if refs:
            references[key] = refs
            all_referenced.update(refs)

    defined = set(env.keys())
    undefined = all_referenced - defined
    unreferenced = defined - all_referenced

    return ReferenceResult(
        references=references,
        undefined=undefined,
        unreferenced=unreferenced,
    )
