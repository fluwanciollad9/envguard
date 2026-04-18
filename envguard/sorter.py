"""Sort .env file keys alphabetically or by custom group order."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    order: List[str]

    @property
    def was_changed(self) -> bool:
        return list(self.original.keys()) != self.order


def sort_env(
    env: Dict[str, str],
    groups: Optional[List[List[str]]] = None,
) -> SortResult:
    """Sort env keys.

    If *groups* is provided each inner list defines an ordered group;
    keys not mentioned appear alphabetically at the end.
    """
    if groups:
        seen: set = set()
        order: List[str] = []
        for group in groups:
            for key in group:
                if key in env and key not in seen:
                    order.append(key)
                    seen.add(key)
        for key in sorted(env.keys()):
            if key not in seen:
                order.append(key)
    else:
        order = sorted(env.keys())

    sorted_env = {k: env[k] for k in order}
    return SortResult(original=dict(env), sorted_env=sorted_env, order=order)


def render_sorted(result: SortResult) -> str:
    """Render a SortResult back to .env file text."""
    lines = [f"{k}={v}" for k, v in result.sorted_env.items()]
    return "\n".join(lines) + "\n"
