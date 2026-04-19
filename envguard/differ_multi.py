"""Compare multiple .env files simultaneously and report cross-environment differences."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class MultiDiffResult:
    envs: Dict[str, Dict[str, str]]  # label -> parsed env
    all_keys: Set[str] = field(default_factory=set)

    def __post_init__(self):
        for env in self.envs.values():
            self.all_keys.update(env.keys())

    def missing_in(self, label: str) -> List[str]:
        """Keys present in other envs but missing in *label*."""
        env = self.envs.get(label, {})
        return sorted(k for k in self.all_keys if k not in env)

    def value_differences(self) -> Dict[str, Dict[str, str]]:
        """Keys whose values differ across at least two envs.
        Returns {key: {label: value_or_MISSING}}.
        """
        result: Dict[str, Dict[str, str]] = {}
        for key in self.all_keys:
            values = {label: env.get(key, "<MISSING>") for label, env in self.envs.items()}
            if len(set(values.values())) > 1:
                result[key] = values
        return result

    def common_keys(self) -> List[str]:
        """Keys present in every env."""
        if not self.envs:
            return []
        sets = [set(env.keys()) for env in self.envs.values()]
        return sorted(set.intersection(*sets))

    def has_differences(self) -> bool:
        return bool(self.value_differences()) or any(
            self.missing_in(label) for label in self.envs
        )


def diff_multiple(envs: Dict[str, Dict[str, str]]) -> MultiDiffResult:
    """Build a MultiDiffResult from a mapping of label -> parsed env dict."""
    return MultiDiffResult(envs=envs)
