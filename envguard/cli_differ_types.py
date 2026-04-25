"""CLI command: envguard typediff — compare inferred value types between two .env files."""
from __future__ import annotations

import json
import sys

import click

from envguard.differ_types import diff_types
from envguard.parser import parse_env_file


def _render_text(result) -> str:
    lines: list[str] = []
    if result.changed:
        lines.append("Type changes:")
        for entry in result.changed:
            lines.append(f"  {entry}")
    if result.only_in_source:
        lines.append(f"Only in {result.source_label}:")
        for key in result.only_in_source:
            lines.append(f"  {key}")
    if result.only_in_target:
        lines.append(f"Only in {result.target_label}:")
        for key in result.only_in_target:
            lines.append(f"  {key}")
    if not lines:
        lines.append("No type differences found.")
    return "\n".join(lines)


def _render_json(result) -> str:
    data = {
        "source": result.source_label,
        "target": result.target_label,
        "changed": [
            {"key": e.key, "source_type": e.source_type, "target_type": e.target_type}
            for e in result.changed
        ],
        "only_in_source": result.only_in_source,
        "only_in_target": result.only_in_target,
        "summary": result.summary(),
    }
    return json.dumps(data, indent=2)


@click.command("typediff")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--strict", is_flag=True, help="Exit non-zero if any type differences are found.")
def typediff_cmd(source: str, target: str, fmt: str, strict: bool) -> None:
    """Compare inferred value types between SOURCE and TARGET .env files."""
    src_env = parse_env_file(source)
    tgt_env = parse_env_file(target)
    result = diff_types(src_env, tgt_env, source_label=source, target_label=target)

    if fmt == "json":
        click.echo(_render_json(result))
    else:
        click.echo(_render_text(result))

    if strict and result.has_differences():
        sys.exit(1)
