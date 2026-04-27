"""Detect encoding differences between two .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import chardet


@dataclass
class EncodingDiffEntry:
    key: str
    source_encoding: Optional[str]
    target_encoding: Optional[str]

    def __str__(self) -> str:
        return (
            f"{self.key}: {self.source_encoding!r} -> {self.target_encoding!r}"
        )


@dataclass
class EncodingDiffResult:
    source_file: str
    target_file: str
    source_file_encoding: Optional[str]
    target_file_encoding: Optional[str]
    changed: List[EncodingDiffEntry] = field(default_factory=list)
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(
            self.changed
            or self.only_in_source
            or self.only_in_target
            or self.source_file_encoding != self.target_file_encoding
        )

    def summary(self) -> str:
        parts: List[str] = []
        if self.source_file_encoding != self.target_file_encoding:
            parts.append(
                f"file encoding: {self.source_file_encoding!r} -> {self.target_file_encoding!r}"
            )
        if self.changed:
            parts.append(f"{len(self.changed)} value encoding change(s)")
        if self.only_in_source:
            parts.append(f"{len(self.only_in_source)} key(s) only in source")
        if self.only_in_target:
            parts.append(f"{len(self.only_in_target)} key(s) only in target")
        return "; ".join(parts) if parts else "no encoding differences"


def _detect_encoding(raw: bytes) -> Optional[str]:
    result = chardet.detect(raw)
    return result.get("encoding")


def _value_encodings(env: Dict[str, str]) -> Dict[str, Optional[str]]:
    return {
        key: _detect_encoding(value.encode("utf-8", errors="replace"))
        for key, value in env.items()
    }


def diff_encoding(
    source_path: str,
    target_path: str,
    source_env: Dict[str, str],
    target_env: Dict[str, str],
) -> EncodingDiffResult:
    with open(source_path, "rb") as fh:
        src_file_enc = _detect_encoding(fh.read())
    with open(target_path, "rb") as fh:
        tgt_file_enc = _detect_encoding(fh.read())

    src_encs = _value_encodings(source_env)
    tgt_encs = _value_encodings(target_env)

    src_keys = set(source_env)
    tgt_keys = set(target_env)

    changed: List[EncodingDiffEntry] = []
    for key in src_keys & tgt_keys:
        if src_encs[key] != tgt_encs[key]:
            changed.append(EncodingDiffEntry(key, src_encs[key], tgt_encs[key]))

    return EncodingDiffResult(
        source_file=source_path,
        target_file=target_path,
        source_file_encoding=src_file_enc,
        target_file_encoding=tgt_file_enc,
        changed=sorted(changed, key=lambda e: e.key),
        only_in_source=sorted(src_keys - tgt_keys),
        only_in_target=sorted(tgt_keys - src_keys),
    )
