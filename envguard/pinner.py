"""Pin environment variable values to a lockfile for drift detection."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class PinResult:
    pinned: Dict[str, str]
    drifted: List[str] = field(default_factory=list)
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    def has_drift(self) -> bool:
        return bool(self.drifted or self.new_keys or self.removed_keys)

    def summary(self) -> str:
        parts = []
        if self.drifted:
            parts.append(f"{len(self.drifted)} drifted")
        if self.new_keys:
            parts.append(f"{len(self.new_keys)} new")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed")
        return ", ".join(parts) if parts else "no drift detected"


def pin_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a lockfile dict from the current env."""
    return dict(env)


def check_drift(env: Dict[str, str], lock: Dict[str, str]) -> PinResult:
    """Compare env against a previously pinned lockfile."""
    drifted = [k for k in env if k in lock and env[k] != lock[k]]
    new_keys = [k for k in env if k not in lock]
    removed_keys = [k for k in lock if k not in env]
    return PinResult(pinned=lock, drifted=drifted, new_keys=new_keys, removed_keys=removed_keys)


def save_lock(lock: Dict[str, str], path: Path) -> None:
    path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_lock(path: Path) -> Dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Lock file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
