"""CLI command: envguard section-diff <source> <target>"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.differ_sections import SectionDiffResult, diff_sections


def _render_text(result: SectionDiffResult) -> str:
    if not result.has_differences:
        return "No section differences found."
    lines = []
    for section, diff in result.diffs.items():
        if not diff.has_differences:
            continue
        lines.append(f"\n{section}")
        for key in diff.only_in_source:
            lines.append(f"  - {key}  (only in source)")
        for key in diff.only_in_target:
            lines.append(f"  + {key}  (only in target)")
        for key, src, tgt in diff.modified:
            lines.append(f"  ~ {key}: {src!r} -> {tgt!r}")
    for s in result.sections_only_in_source:
        lines.append(f"\nSection only in source: {s}")
    for s in result.sections_only_in_target:
        lines.append(f"\nSection only in target: {s}")
    return "\n".join(lines)


def _render_json(result: SectionDiffResult) -> str:
    data: dict = {
        "has_differences": result.has_differences,
        "sections_only_in_source": result.sections_only_in_source,
        "sections_only_in_target": result.sections_only_in_target,
        "diffs": {},
    }
    for section, diff in result.diffs.items():
        data["diffs"][section] = {
            "only_in_source": diff.only_in_source,
            "only_in_target": diff.only_in_target,
            "modified": [
                {"key": k, "source": s, "target": t}
                for k, s, t in diff.modified
            ],
        }
    return json.dumps(data, indent=2)


@click.command("section-diff")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--strict", is_flag=True, help="Exit 1 if differences found.")
def section_diff_cmd(source: str, target: str, fmt: str, strict: bool) -> None:
    """Diff two .env files by their comment-delimited sections."""
    src_lines = Path(source).read_text().splitlines(keepends=True)
    tgt_lines = Path(target).read_text().splitlines(keepends=True)
    result = diff_sections(src_lines, tgt_lines)

    if fmt == "json":
        click.echo(_render_json(result))
    else:
        click.echo(_render_text(result))

    if strict and result.has_differences:
        sys.exit(1)
