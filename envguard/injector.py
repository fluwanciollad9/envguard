"""Inject key=value pairs into an existing env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping


@dataclass
class InjectResult:
    env: Dict[str, str]
    injected: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)


def was_changed(result: InjectResult) -> bool:
    return bool(result.injected or result.overwritten)


def inject_env(
    base: Mapping[str, str],
    overrides: Mapping[str, str],
    *,
    allow_overwrite: bool = True,
) -> InjectResult:
    """Inject *overrides* into *base*.

    Parameters
    ----------
    base:            Original env mapping.
    overrides:       Key/value pairs to inject.
    allow_overwrite: When False, existing keys are skipped (not overwritten).
    """
    env = dict(base)
    injected: List[str] = []
    overwritten: List[str] = []

    for key, value in overrides.items():
        if key in env:
            if allow_overwrite:
                overwritten.append(key)
                env[key] = value
        else:
            injected.append(key)
            env[key] = value

    return InjectResult(env=env, injected=sorted(injected), overwritten=sorted(overwritten))


def render_injected(result: InjectResult) -> str:
    """Render the resulting env as .env file text."""
    return "\n".join(f"{k}={v}" for k, v in sorted(result.env.items())) + "\n"
