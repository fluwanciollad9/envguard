"""Diff logic for comparing two parsed .env dictionaries."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    missing_keys: List[str] = field(default_factory=list)   # in base, not in target
    extra_keys: List[str] = field(default_factory=list)     # in target, not in base
    changed_keys: Dict[str, tuple] = field(default_factory=dict)  # key -> (base_val, target_val)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing_keys or self.extra_keys or self.changed_keys)


def diff_envs(
    base: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
) -> DiffResult:
    """Compare two env dicts and return a DiffResult."""
    result = DiffResult()

    base_keys = set(base.keys())
    target_keys = set(target.keys())

    result.missing_keys = sorted(base_keys - target_keys)
    result.extra_keys = sorted(target_keys - base_keys)

    for key in sorted(base_keys & target_keys):
        if base[key] != target[key]:
            result.changed_keys[key] = (base[key], target[key])

    return result
