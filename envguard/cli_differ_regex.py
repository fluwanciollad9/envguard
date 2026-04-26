"""CLI command: envguard regex-diff SOURCE TARGET --pattern PATTERN."""
from __future__ import annotations

import json
import sys

import click

from envguard.parser import parse_env_file
from envguard.differ_regex import diff_env_by_regex


def _render_text(result) -> str:
    lines = [result.summary()]
    for change in result.changes:
        lines.append(f"  {change}")
    return "\n".join(lines)


def _render_json(result) -> str:
    data = {
        "pattern": result.pattern,
        "matched_keys": result.matched_keys,
        "has_differences": result.has_differences(),
        "changes": [
            {
                "key": c.key,
                "source_value": c.source_value,
                "target_value": c.target_value,
                "status": (
                    "added" if c.is_added()
                    else "removed" if c.is_removed()
                    else "modified"
                ),
            }
            for c in result.changes
        ],
    }
    return json.dumps(data, indent=2)


@click.command("regex-diff")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--pattern", "-p", required=True, help="Regex pattern to filter keys.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--strict", is_flag=True, default=False, help="Exit 1 when differences found.")
def regex_diff_cmd(source: str, target: str, pattern: str, fmt: str, strict: bool) -> None:
    """Diff keys matching PATTERN between SOURCE and TARGET .env files."""
    src_env = parse_env_file(source)
    tgt_env = parse_env_file(target)
    result = diff_env_by_regex(src_env, tgt_env, pattern)

    output = _render_json(result) if fmt == "json" else _render_text(result)
    click.echo(output)

    if strict and result.has_differences():
        sys.exit(1)
