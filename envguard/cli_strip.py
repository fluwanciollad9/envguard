"""CLI command: strip keys from an env file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.parser import parse_env_file
from envguard.stripper import strip_env, render_stripped


@click.command("strip")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("-k", "--key", "keys", multiple=True, required=True, help="Key to strip (repeatable).")
@click.option("--in-place", is_flag=True, help="Overwrite the file in place.")
@click.option("--dry-run", is_flag=True, help="Show what would be removed without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "dotenv", "json"]), default="dotenv")
def strip_cmd(envfile: str, keys: tuple, in_place: bool, dry_run: bool, fmt: str) -> None:
    """Strip one or more keys from an env file."""
    env = parse_env_file(envfile)
    result = strip_env(env, list(keys))

    if fmt == "json":
        click.echo(json.dumps({
            "removed": result.removed,
            "not_found": result.not_found,
            "was_changed": result.was_changed(),
            "stripped": result.stripped,
        }, indent=2))
    elif fmt == "text":
        click.echo(result.summary())
        if result.not_found:
            click.echo(f"Warning: keys not found: {', '.join(result.not_found)}", err=True)
    else:  # dotenv
        click.echo(render_stripped(result.stripped), nl=False)

    if result.not_found and fmt != "json":
        sys.exit(0)  # not_found is advisory only

    if in_place and not dry_run and result.was_changed():
        Path(envfile).write_text(render_stripped(result.stripped))
    elif dry_run and result.was_changed():
        click.echo(f"[dry-run] would remove: {', '.join(result.removed)}", err=True)
