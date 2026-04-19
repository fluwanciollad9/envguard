"""CLI sub-command: envguard defaults"""
from __future__ import annotations
import json
imlib import Path

import click

from .parser import parse_env_file
from .defaults import apply_defaults
from .renderer import render_env  # simple key=value renderer (see below)


@click.command("defaults")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--set", "pairs", multiple=True, metavar="KEY=VALUE",
    help="Default key=value pair (repeatable).",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--in-place", is_flag=True, default=False, help="Write result back to file.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def defaults_cmd(env_file: str, pairs: tuple, overwrite: bool, in_place: bool, fmt: str) -> None:
    """Apply default values to missing keys in ENV_FILE."""
    if not pairs:
        click.echo("No defaults provided. Use --set KEY=VALUE.", err=True)
        sys.exit(1)

    defaults: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid pair (missing '='): {pair}", err=True)
            sys.exit(1)
        k, v = pair.split("=", 1)
        defaults[k.strip()] = v.strip()

    env = parse_env_file(Path(env_file))
    result = apply_defaults(env, defaults, overwrite=overwrite)

    if fmt == "json":
        click.echo(json.dumps({
            "applied": result.applied,
            "skipped": result.skipped,
            "env": result.env,
        }, indent=2))
    else:
        rendered = render_env(result.env)
        if in_place:
            Path(env_file).write_text(rendered)
            click.echo(result.summary())
        else:
            click.echo(rendered)

    sys.exit(0)
