"""CLI command: envguard structure-diff SOURCE TARGET."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.parser import parse_env_file
from envguard.differ_structure import diff_structure


def _render_text(result) -> str:
    lines: list[str] = []
    lines.append(f"Source keys : {result.source_key_count}")
    lines.append(f"Target keys : {result.target_key_count}")
    if result.only_in_source:
        lines.append("Only in source  : " + ", ".join(result.only_in_source))
    if result.only_in_target:
        lines.append("Only in target  : " + ", ".join(result.only_in_target))
    if result.source_empty_keys:
        lines.append("Empty in source : " + ", ".join(result.source_empty_keys))
    if result.target_empty_keys:
        lines.append("Empty in target : " + ", ".join(result.target_empty_keys))
    if result.type_changes:
        for key, (src_t, tgt_t) in sorted(result.type_changes.items()):
            lines.append(f"Type change     : {key}  {src_t} -> {tgt_t}")
    if not result.has_differences():
        lines.append("No structural differences.")
    return "\n".join(lines)


def _render_json(result) -> str:
    data = {
        "source_key_count": result.source_key_count,
        "target_key_count": result.target_key_count,
        "only_in_source": result.only_in_source,
        "only_in_target": result.only_in_target,
        "source_empty_keys": result.source_empty_keys,
        "target_empty_keys": result.target_empty_keys,
        "type_changes": {
            k: {"source": v[0], "target": v[1]}
            for k, v in result.type_changes.items()
        },
        "has_differences": result.has_differences(),
    }
    return json.dumps(data, indent=2)


@click.command("structure-diff")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 when structural differences are found.",
)
def structure_diff_cmd(source: str, target: str, fmt: str, strict: bool) -> None:
    """Compare the structure of two .env files."""
    src_env = parse_env_file(Path(source))
    tgt_env = parse_env_file(Path(target))
    result = diff_structure(src_env, tgt_env)

    if fmt == "json":
        click.echo(_render_json(result))
    else:
        click.echo(_render_text(result))

    if strict and result.has_differences():
        sys.exit(1)
