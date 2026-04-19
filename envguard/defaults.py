"""Apply default values to missing keys in an env dict."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DefaultsResult:
    env: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def was_changed(self) -> bool:
        return len(self.applied) > 0

    def summary(self) -> str:
        lines = []
        if self.applied:
            lines.append(f"Applied defaults for: {', '.join(self.applied)}")
        if self.skipped:
            lines.append(f"Skipped (already set): {', '.join(self.skipped)}")
        if not lines:
            return "No defaults to apply."
        return "\n".join(lines)


def apply_defaults(
    env: Dict[str, str],
    defaults: Dict[str, str],
    overwrite: bool = False,
) -> DefaultsResult:
    """Merge *defaults* into *env*.

    By default only missing keys are filled in.  Pass ``overwrite=True`` to
    replace existing values as well.
    """
    result_env = dict(env)
    applied: List[str] = []
    skipped: List[str] = []

    for key, value in defaults.items():
        if key in result_env and not overwrite:
            skipped.append(key)
        else:
            if key in result_env:
                skipped_note = False
            else:
                skipped_note = False
            result_env[key] = value
            applied.append(key)

    return DefaultsResult(env=result_env, applied=applied, skipped=skipped)
