"""CLI command: envguard template — generate a .env template from a schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.templater import generate_template, render_template


@click.command("template")
@click.argument("schema", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output", "-o",
    default=None,
    help="Write template to this file instead of stdout.",
)
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json"]),
    default="dotenv",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--summary", "show_summary",
    is_flag=True,
    default=False,
    help="Print a summary to stderr.",
)
def template_cmd(schema: str, output: str | None, fmt: str, show_summary: bool) -> None:
    """Generate a .env template from SCHEMA."""
    try:
        result = generate_template(schema)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if fmt == "json":
        text = json.dumps(result.rendered, indent=2)
    else:
        text = render_template(result)

    if output:
        Path(output).write_text(text)
        click.echo(f"Template written to {output}", err=True)
    else:
        click.echo(text, nl=False)

    if show_summary:
        click.echo(result.summary(), err=True)
