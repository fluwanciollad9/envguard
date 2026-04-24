"""CLI command: envguard prune — remove env keys by value pattern or emptiness."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from envguard.parser import parse_env_file
from envguard.pruner import prune_env, render_pruned


@click.command("prune")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--pattern", "-p", default=None, help="Regex matched against values; matching keys are removed.")
@click.option("--empty", is_flag=True, default=False, help="Remove keys with empty values.")
@click.option("--key", "-k", multiple=True, help="Explicit key name(s) to remove (repeatable).")
@click.option("--in-place", is_flag=True, default=False, help="Overwrite the source file.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be removed without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "json", "dotenv"]), default="text")
def prune_cmd(
    env_file: str,
    pattern: Optional[str],
    empty: bool,
    key: tuple,
    in_place: bool,
    dry_run: bool,
    fmt: str,
) -> None:
    """Remove keys from ENV_FILE by value pattern, emptiness, or explicit name."""
    if not pattern and not empty and not key:
        raise click.UsageError("Provide --pattern, --empty, or at least one --key.")

    env = parse_env_file(env_file)
    result = prune_env(
        env,
        pattern=pattern or None,
        empty_only=empty,
        keys=list(key) if key else None,
    )

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "removed": result.removed,
                    "remaining": result.pruned,
                    "was_changed": result.was_changed(),
                },
                indent=2,
            )
        )
    elif fmt == "dotenv":
        click.echo(render_pruned(result.pruned), nl=False)
    else:
        if result.was_changed():
            for k in result.removed:
                click.echo(f"  - {k}")
            click.echo(result.summary())
        else:
            click.echo("Nothing to prune.")

    if result.was_changed() and in_place and not dry_run:
        Path(env_file).write_text(render_pruned(result.pruned))

    sys.exit(0)
