"""Add, remove, or list inline and full-line comments in .env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class CommentResult:
    lines: List[str]  # final rendered lines
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    comments: Dict[str, str] = field(default_factory=dict)  # key -> comment text


def was_changed(result: CommentResult) -> bool:
    return bool(result.added or result.removed)


def _parse_lines(lines: List[str]) -> List[Tuple[str, str, str]]:
    """Return list of (raw_line, key_or_none, existing_comment)."""
    parsed = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            parsed.append((stripped, None, ""))
            continue
        if "=" not in stripped:
            parsed.append((stripped, None, ""))
            continue
        key, _, rest = stripped.partition("=")
        key = key.strip()
        comment = ""
        if " #" in rest:
            idx = rest.index(" #")
            comment = rest[idx + 1:].strip()
        parsed.append((stripped, key, comment))
    return parsed


def add_comments(env_lines: List[str], annotations: Dict[str, str]) -> CommentResult:
    """Append or replace inline comment for specified keys."""
    parsed = _parse_lines(env_lines)
    out_lines: List[str] = []
    added: List[str] = []
    comments: Dict[str, str] = {}
    for raw, key, existing in parsed:
        if key and key in annotations:
            base = raw.split(" #")[0].rstrip() if " #" in raw else raw
            new_line = f"{base}  # {annotations[key]}"
            out_lines.append(new_line)
            added.append(key)
            comments[key] = annotations[key]
        else:
            out_lines.append(raw)
            if key and existing:
                comments[key] = existing
    return CommentResult(lines=out_lines, added=added, comments=comments)


def remove_comments(env_lines: List[str], keys: List[str] | None = None) -> CommentResult:
    """Remove inline comments. If keys is None, remove from all keys."""
    parsed = _parse_lines(env_lines)
    out_lines: List[str] = []
    removed: List[str] = []
    for raw, key, existing in parsed:
        if key and existing and (keys is None or key in keys):
            base = raw.split(" #")[0].rstrip()
            out_lines.append(base)
            removed.append(key)
        else:
            out_lines.append(raw)
    return CommentResult(lines=out_lines, removed=removed)


def list_comments(env_lines: List[str]) -> Dict[str, str]:
    """Return mapping of key -> inline comment for all keys that have one."""
    parsed = _parse_lines(env_lines)
    return {key: comment for _, key, comment in parsed if key and comment}
