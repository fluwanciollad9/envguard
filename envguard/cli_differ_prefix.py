"""CLI command: envguard prefix-diff <source> <target>"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.differ_prefix import diff_prefixes
from envguard.parser import parse_env_file


def _render_text(result) -> str:
    lines: list[str] = []
    if result.only_in_source:
        for p in sorted(result.only_in_source):
            keys = ", ".join(sorted(result.source_map[p]))
            lines.append(f"  source-only prefix '{p}': {keys}")
    if result.only_in_target:
        for p in sorted(result.only_in_target):
            keys = ", ".join(sorted(result.target_map[p]))
            lines.append(f"  target-only prefix '{p}': {keys}")
    if result.common:
        for p in sorted(result.common):
            lines.append(f"  shared prefix '{p}'")
    return "\n".join(lines)


def _render_json(result) -> str:
    data = {
        "has_differences": result.has_differences(),
        "summary": result.summary(),
        "only_in_source": sorted(result.only_in_source),
        "only_in_target": sorted(result.only_in_target),
        "common": sorted(result.common),
        "source_map": {k: sorted(v) for k, v in result.source_map.items()},
        "target_map": {k: sorted(v) for k, v in result.target_map.items()},
    }
    return json.dumps(data, indent=2)


@click.command("prefix-diff")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
@click.option("--strict", is_flag=True, default=False,
              help="Exit non-zero when prefix sets differ.")
def prefix_diff_cmd(source: str, target: str, fmt: str, strict: bool) -> None:
    """Show prefix-level differences between SOURCE and TARGET .env files."""
    src_env = parse_env_file(Path(source))
    tgt_env = parse_env_file(Path(target))
    result = diff_prefixes(src_env, tgt_env)

    if fmt == "json":
        click.echo(_render_json(result))
    else:
        click.echo(f"Prefix diff: {result.summary()}")
        body = _render_text(result)
        if body:
            click.echo(body)

    if strict and result.has_differences():
        sys.exit(1)
