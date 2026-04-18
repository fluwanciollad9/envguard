from __future__ import annotations
import json
import sys
import click
from envguard.duplicates import find_duplicates


@click.command("duplicates")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if duplicates found.")
def duplicates_cmd(envfile: str, fmt: str, strict: bool) -> None:
    """Find duplicate keys in ENVFILE."""
    result = find_duplicates(envfile)

    if fmt == "json":
        data = {
            "has_duplicates": result.has_duplicates(),
            "duplicates": {k: v for k, v in result.duplicates.items()},
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(result.summary())

    if strict and result.has_duplicates():
        sys.exit(1)
