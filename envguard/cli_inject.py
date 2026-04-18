"""CLI command: envguard inject — inject key=value pairs into a .env file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.injector import inject_env, render_injected, was_changed
from envguard.parser import parse_env_file


@click.command("inject")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("pairs", nargs=-1, metavar="KEY=VALUE...")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys that already exist.")
@click.option("--in-place", is_flag=True, default=False, help="Write result back to ENV_FILE.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would change without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def inject_cmd(
    env_file: str,
    pairs: tuple[str, ...],
    no_overwrite: bool,
    in_place: bool,
    dry_run: bool,
    fmt: str,
) -> None:
    """Inject KEY=VALUE pairs into ENV_FILE."""
    overrides: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid pair (missing '='): {pair}", err=True)
            sys.exit(2)
        k, _, v = pair.partition("=")
        overrides[k.strip()] = v.strip()

    base = parse_env_file(Path(env_file))
    result = inject_env(base, overrides, allow_overwrite=not no_overwrite)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "injected": result.injected,
                    "overwritten": result.overwritten,
                    "changed": was_changed(result),
                },
                indent=2,
            )
        )
    else:
        if result.injected:
            click.echo(f"Injected:    {', '.join(result.injected)}")
        if result.overwritten:
            click.echo(f"Overwritten: {', '.join(result.overwritten)}")
        if not was_changed(result):
            click.echo("No changes.")

    if in_place and not dry_run and was_changed(result):
        Path(env_file).write_text(render_injected(result))
        click.echo(f"Written to {env_file}")
