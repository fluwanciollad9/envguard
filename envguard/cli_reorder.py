"""CLI command: envguard reorder — reorder keys in a .env file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.parser import parse_env_file
from envguard.reorderer import reorder_env, render_reordered


@click.command("reorder")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--key",
    "keys",
    multiple=True,
    required=True,
    help="Key name in desired position (repeatable, defines order).",
)
@click.option(
    "--drop-unrecognised",
    is_flag=True,
    default=False,
    help="Drop keys that are not listed in --key instead of appending them.",
)
@click.option(
    "--in-place", "-i",
    is_flag=True,
    default=False,
    help="Write result back to ENV_FILE.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would change without writing anything.",
)
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json", "text"]),
    default="dotenv",
    show_default=True,
)
def reorder_cmd(
    env_file: str,
    keys: tuple,
    drop_unrecognised: bool,
    in_place: bool,
    dry_run: bool,
    fmt: str,
) -> None:
    """Reorder keys in ENV_FILE according to the order given by --key flags."""
    env = parse_env_file(env_file)
    result = reorder_env(env, list(keys), append_unrecognised=not drop_unrecognised)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "reordered": result.reordered,
                    "unrecognised": result.unrecognised,
                    "missing": result.missing,
                    "was_changed": result.was_changed(),
                },
                indent=2,
            )
        )
    elif fmt == "text":
        click.echo(result.summary())
        if result.unrecognised:
            click.echo("Appended (not in order): " + ", ".join(result.unrecognised))
        if result.missing:
            click.echo("Not found in env: " + ", ".join(result.missing))
    else:  # dotenv
        rendered = render_reordered(result)
        if in_place and not dry_run:
            Path(env_file).write_text(rendered)
        else:
            click.echo(rendered, nl=False)

    if dry_run and result.was_changed():
        click.echo("[dry-run] File would be modified.", err=True)

    sys.exit(0)
