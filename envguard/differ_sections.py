"""Diff two .env files grouped by logical sections (comment-delimited blocks)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


def _parse_sections(lines: List[str]) -> Dict[str, Dict[str, str]]:
    """Return {section_header: {key: value}} from raw file lines."""
    sections: Dict[str, Dict[str, str]] = {}
    current: str = "__default__"
    sections[current] = {}

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            current = stripped
            if current not in sections:
                sections[current] = {}
        elif "=" in stripped and stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition("=")
            sections[current][key.strip()] = value.strip()

    return sections


@dataclass
class SectionDiff:
    section: str
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)
    modified: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, src, tgt)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_source or self.only_in_target or self.modified)

    def summary(self) -> str:
        parts = []
        if self.only_in_source:
            parts.append(f"+{len(self.only_in_source)} only-in-source")
        if self.only_in_target:
            parts.append(f"+{len(self.only_in_target)} only-in-target")
        if self.modified:
            parts.append(f"{len(self.modified)} modified")
        return f"[{self.section}] " + (" | ".join(parts) if parts else "identical")


@dataclass
class SectionDiffResult:
    diffs: Dict[str, SectionDiff] = field(default_factory=dict)
    sections_only_in_source: List[str] = field(default_factory=list)
    sections_only_in_target: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return (
            bool(self.sections_only_in_source)
            or bool(self.sections_only_in_target)
            or any(d.has_differences for d in self.diffs.values())
        )

    def summary(self) -> str:
        lines = []
        for d in self.diffs.values():
            lines.append(d.summary())
        for s in self.sections_only_in_source:
            lines.append(f"Section only in source: {s}")
        for s in self.sections_only_in_target:
            lines.append(f"Section only in target: {s}")
        return "\n".join(lines) if lines else "No section differences."


def diff_sections(
    source_lines: List[str],
    target_lines: List[str],
) -> SectionDiffResult:
    src_sections = _parse_sections(source_lines)
    tgt_sections = _parse_sections(target_lines)

    all_sections = set(src_sections) | set(tgt_sections)
    result = SectionDiffResult()

    for section in all_sections:
        in_src = section in src_sections
        in_tgt = section in tgt_sections
        if in_src and not in_tgt:
            result.sections_only_in_source.append(section)
            continue
        if in_tgt and not in_src:
            result.sections_only_in_target.append(section)
            continue

        src_kv = src_sections[section]
        tgt_kv = tgt_sections[section]
        diff = SectionDiff(section=section)
        all_keys = set(src_kv) | set(tgt_kv)
        for key in all_keys:
            if key in src_kv and key not in tgt_kv:
                diff.only_in_source.append(key)
            elif key in tgt_kv and key not in src_kv:
                diff.only_in_target.append(key)
            elif src_kv[key] != tgt_kv[key]:
                diff.modified.append((key, src_kv[key], tgt_kv[key]))
        result.diffs[section] = diff

    return result
