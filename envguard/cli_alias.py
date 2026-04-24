"""cli_alias.py – CLI command for aliasing keys in a .env file."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from envguard.aliaser import alias_env, summary, was_changed
from envguard.parser import parse_env_file
from envguard.renamer import render_renamed  # reuse dotenv renderer


def _render(env: dict) -> str:
    lines = [f"{k}={v}" for k, v in env.items()]
    return "\n".join(lines) + ("\n" if lines else "")


@click.command("alias")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--map",
    "alias_pairs",
    multiple=True,
    metavar="SRC:ALIAS",
    required=True,
    help="Alias mapping as SOURCE_KEY:ALIAS_KEY.  Repeatable.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing alias keys.")
@click.option("--remove-original", is_flag=True, default=False, help="Remove the source key after aliasing.")
@click.option("--in-place", is_flag=True, default=False, help="Write result back to the file.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would change without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "dotenv", "json"]), default="dotenv")
def alias_cmd(
    env_file: str,
    alias_pairs: tuple,
    overwrite: bool,
    remove_original: bool,
    in_place: bool,
    dry_run: bool,
    fmt: str,
) -> None:
    """Create alias keys for existing keys in ENV_FILE."""
    alias_map: dict = {}
    for pair in alias_pairs:
        if ":" not in pair:
            raise click.BadParameter(f"Expected SRC:ALIAS, got {pair!r}", param_hint="--map")
        src, alias = pair.split(":", 1)
        alias_map[src.strip()] = alias.strip()

    env = parse_env_file(env_file)
    result = alias_env(env, alias_map, overwrite=overwrite, keep_original=not remove_original)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "applied": result.applied,
                    "skipped": result.skipped,
                    "conflicts": result.conflicts,
                    "env": result.env,
                },
                indent=2,
            )
        )
    elif fmt == "text":
        click.echo(summary(result))
        for k in result.applied:
            click.echo(f"  + {k}")
        for k in result.conflicts:
            click.echo(f"  ! conflict: {k} (not overwritten)")
    else:
        click.echo(_render(result.env), nl=False)

    if in_place and not dry_run:
        Path(env_file).write_text(_render(result.env))

    if result.conflicts:
        sys.exit(1)
