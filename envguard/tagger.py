"""Tag env keys with arbitrary labels and filter by tag."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class TagResult:
    tags: Dict[str, Set[str]]          # key -> set of tags
    tagged_count: int
    untagged_keys: List[str]

    def keys_for_tag(self, tag: str) -> List[str]:
        return [k for k, ts in self.tags.items() if tag in ts]

    def tags_for_key(self, key: str) -> Set[str]:
        return self.tags.get(key, set())

    def summary(self) -> str:
        lines = [f"Tagged keys: {self.tagged_count}"]
        if self.untagged_keys:
            lines.append(f"Untagged keys: {len(self.untagged_keys)}")
        return "\n".join(lines)


def tag_env(
    env: Dict[str, str],
    tag_map: Dict[str, List[str]],
) -> TagResult:
    """Apply tags from tag_map {tag: [key, ...]} to env keys.

    Keys not present in env are silently skipped.
    """
    tags: Dict[str, Set[str]] = {k: set() for k in env}

    for tag, keys in tag_map.items():
        for key in keys:
            if key in tags:
                tags[key].add(tag)

    tagged_count = sum(1 for ts in tags.values() if ts)
    untagged_keys = [k for k, ts in tags.items() if not ts]

    return TagResult(
        tags=tags,
        tagged_count=tagged_count,
        untagged_keys=untagged_keys,
    )


def filter_by_tag(
    env: Dict[str, str],
    result: TagResult,
    tag: str,
) -> Dict[str, str]:
    """Return subset of env whose keys carry the given tag."""
    matching = result.keys_for_tag(tag)
    return {k: env[k] for k in matching if k in env}
