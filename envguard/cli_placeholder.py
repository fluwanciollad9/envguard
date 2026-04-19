"""CLI command: envguard placeholder — detect unfilled placeholder values."""
from __future__ import annotations
import json
import sys
import click
from envguard.parser import parse_env_file
from envguard.placeholder import find_placeholders


@click.command("placeholder")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Exit non-zero when placeholders are found.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
def placeholder_cmd(env_file: str, strict: bool, fmt: str) -> None:
    """Detect keys with unfilled placeholder values in ENV_FILE."""
    env = parse_env_file(env_file)
    result = find_placeholders(env)

    if fmt == "json":
        click.echo(json.dumps({
            "file": env_file,
            "has_placeholders": result.has_placeholders,
            "placeholders": result.found,
        }, indent=2))
    else:
        if result.has_placeholders:
            click.echo(result.summary())
        else:
            click.echo("No placeholder values detected.")

    if strict and result.has_placeholders:
        sys.exit(1)
