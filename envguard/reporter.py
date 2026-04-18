"""Format and output diff/validation results for human or machine consumption."""
from __future__ import annotations

import json
from typing import Literal

from envguard.differ import DiffResult
from envguard.validator import ValidationResult

OutputFormat = Literal["text", "json"]


def _diff_to_dict(result: DiffResult) -> dict:
    return {
        "missing_in_target": sorted(result.missing_in_target),
        "extra_in_target": sorted(result.extra_in_target),
        "changed_values": {k: {"source": v[0], "target": v[1]} for k, v in result.changed_values.items()},
    }


def _validation_to_dict(result: ValidationResult) -> dict:
    return {
        "missing_required": sorted(result.missing_required),
        "empty_required": sorted(result.empty_required),
        "unknown_keys": sorted(result.unknown_keys),
    }


def format_diff(result: DiffResult, fmt: OutputFormat = "text") -> str:
    if fmt == "json":
        return json.dumps(_diff_to_dict(result), indent=2)

    lines: list[str] = []
    for key in sorted(result.missing_in_target):
        lines.append(f"- MISSING   {key}")
    for key in sorted(result.extra_in_target):
        lines.append(f"+ EXTRA     {key}")
    for key, (src, tgt) in sorted(result.changed_values.items()):
        lines.append(f"~ CHANGED   {key}  ({src!r} -> {tgt!r})")
    return "\n".join(lines) if lines else "No differences found."


def format_validation(result: ValidationResult, fmt: OutputFormat = "text") -> str:
    if fmt == "json":
        return json.dumps(_validation_to_dict(result), indent=2)

    lines: list[str] = []
    for key in sorted(result.missing_required):
        lines.append(f"✗ MISSING   {key}")
    for key in sorted(result.empty_required):
        lines.append(f"✗ EMPTY     {key}")
    for key in sorted(result.unknown_keys):
        lines.append(f"? UNKNOWN   {key}")
    return "\n".join(lines) if lines else "Validation passed."
