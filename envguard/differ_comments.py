"""Compare inline comments between two .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


_COMMENT_RE = re.compile(r"(?<!\\)#(.*)$")


def _extract_comment(line: str) -> Optional[str]:
    """Return the inline comment text (stripped) or None."""
    m = _COMMENT_RE.search(line)
    if m:
        return m.group(1).strip()
    return None


def _parse_comments(path: Path) -> Dict[str, Optional[str]]:
    """Return a mapping of key -> inline comment (or None) for each key."""
    result: Dict[str, Optional[str]] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, rest = line.partition("=")
        key = key.strip()
        result[key] = _extract_comment(rest)
    return result


@dataclass
class CommentDiffEntry:
    key: str
    source_comment: Optional[str]
    target_comment: Optional[str]

    def is_added(self) -> bool:
        return self.source_comment is None and self.target_comment is not None

    def is_removed(self) -> bool:
        return self.source_comment is not None and self.target_comment is None

    def is_modified(self) -> bool:
        return (
            self.source_comment is not None
            and self.target_comment is not None
            and self.source_comment != self.target_comment
        )

    def __str__(self) -> str:
        if self.is_added():
            return f"{self.key}: [no comment] -> '# {self.target_comment}'"
        if self.is_removed():
            return f"{self.key}: '# {self.source_comment}' -> [no comment]"
        return f"{self.key}: '# {self.source_comment}' -> '# {self.target_comment}'"


@dataclass
class CommentDiffResult:
    changes: List[CommentDiffEntry] = field(default_factory=list)
    all_keys: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.changes)

    def summary(self) -> str:
        if not self.has_differences():
            return "No comment differences found."
        parts = []
        added = sum(1 for c in self.changes if c.is_added())
        removed = sum(1 for c in self.changes if c.is_removed())
        modified = sum(1 for c in self.changes if c.is_modified())
        if added:
            parts.append(f"{added} added")
        if removed:
            parts.append(f"{removed} removed")
        if modified:
            parts.append(f"{modified} modified")
        return "Comment differences: " + ", ".join(parts) + "."


def diff_comments(source: Path, target: Path) -> CommentDiffResult:
    """Compare inline comments for all shared keys between source and target."""
    src_comments = _parse_comments(source)
    tgt_comments = _parse_comments(target)
    all_keys = sorted(set(src_comments) | set(tgt_comments))
    changes: List[CommentDiffEntry] = []
    for key in all_keys:
        sc = src_comments.get(key)
        tc = tgt_comments.get(key)
        if sc != tc:
            changes.append(CommentDiffEntry(key=key, source_comment=sc, target_comment=tc))
    return CommentDiffResult(changes=changes, all_keys=all_keys)
