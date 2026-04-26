"""CLI command for age-based env diff."""
from __future__ import annotations

import json
import sys

import click

from envguard.differ_age import diff_age


def _render_text(result) -> str:
    lines = []
    if result.only_in_source:
        lines.append("Only in source:")
        for k in result.only_in_source:
            lines.append(f"  - {k}")
    if result.only_in_target:
        lines.append("Only in target:")
        for k in result.only_in_target:
            lines.append(f"  + {k}")
    if result.changed:
        lines.append("Timestamp differences:")
        for entry in result.changed:
            lines.append(f"  ~ {entry}")
    if not lines:
        lines.append("No age differences detected.")
    return "\n".join(lines)


def _render_json(result) -> str:
    data = {
        "source_file": result.source_file,
        "target_file": result.target_file,
        "only_in_source": result.only_in_source,
        "only_in_target": result.only_in_target,
        "changed": [
            {
                "key": e.key,
                "source_mtime": e.source_mtime,
                "target_mtime": e.target_mtime,
                "delta_seconds": e.delta_seconds,
            }
            for e in result.changed
        ],
        "has_differences": result.has_differences(),
        "summary": result.summary(),
    }
    return json.dumps(data, indent=2)


@click.command("age-diff")
@click.argument("source_ts", metavar="SOURCE_TIMESTAMPS")
@click.argument("target_ts", metavar="TARGET_TIMESTAMPS")
@click.option("--threshold", default=0.0, show_default=True, help="Minimum delta (seconds) to flag.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--strict", is_flag=True, help="Exit 1 if any differences found.")
def age_diff_cmd(source_ts: str, target_ts: str, threshold: float, fmt: str, strict: bool) -> None:
    """Compare two timestamp index files for env key staleness."""
    try:
        result = diff_age(source_ts, target_ts, threshold=threshold)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    if fmt == "json":
        click.echo(_render_json(result))
    else:
        click.echo(_render_text(result))

    if strict and result.has_differences():
        sys.exit(1)
