"""CLI sub-command: interpolate — resolve variable references in a .env file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.parser import parse_env_file
from envguard.interpolator import interpolate


@click.command("interpolate")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--no-os",
    is_flag=True,
    default=False,
    help="Disable fallback to OS environment variables.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["env", "json"]),
    default="env",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any references remain unresolved.",
)
def interpolate_cmd(env_file: str, no_os: bool, fmt: str, strict: bool) -> None:
    """Resolve \$VAR and \${VAR} references inside ENV_FILE and print the result."""
    path = Path(env_file)
    env = parse_env_file(path)
    result = interpolate(env, allow_os=not no_os)

    if fmt == "json":
        click.echo(json.dumps(result.resolved, indent=2))
    else:
        for key, value in result.resolved.items():
            click.echo(f"{key}={value}")

    if result.has_unresolved:
        click.echo(
            f"\nWarning: {len(result.unresolved_keys)} unresolved reference(s): "
            + ", ".join(result.unresolved_keys),
            err=True,
        )
        if strict:
            sys.exit(1)
