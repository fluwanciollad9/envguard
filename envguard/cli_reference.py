"""CLI command: envguard reference — show variable references in an env file."""
from __future__ import annotations

import json
import sys

import click

from envguard.parser import parse_env_file
from envguard.referencer import find_references


@click.command("reference")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any undefined references are found.",
)
def reference_cmd(env_file: str, fmt: str, strict: bool) -> None:
    """Show all variable references (\$VAR / \${VAR}) used in ENV_FILE."""
    env = parse_env_file(env_file)
    result = find_references(env)

    if fmt == "json":
        data = {
            "references": {k: list(v) for k, v in result.references.items()},
            "undefined": sorted(result.undefined),
            "unreferenced": sorted(result.unreferenced),
            "summary": result.summary(),
        }
        click.echo(json.dumps(data, indent=2))
    else:
        if result.references:
            click.echo("References:")
            for key, refs in sorted(result.references.items()):
                click.echo(f"  {key} -> {', '.join(refs)}")
        else:
            click.echo("No variable references found.")

        if result.undefined:
            click.echo("Undefined references:")
            for name in sorted(result.undefined):
                click.echo(f"  {name}")

        if result.unreferenced:
            click.echo("Unreferenced keys:")
            for name in sorted(result.unreferenced):
                click.echo(f"  {name}")

        click.echo(result.summary())

    if strict and result.has_undefined():
        sys.exit(1)
