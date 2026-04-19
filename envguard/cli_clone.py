"""CLI command: envguard clone — clone a .env file with filtering/redaction."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.cloner import clone_env, render_cloned
from envguard.parser import parse_env_file


@click.command("clone")
@click.argument("src", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", type=click.Path(), default=None, help="Write result to file.")
@click.option("--include", multiple=True, metavar="KEY", help="Keys to include (repeatable).")
@click.option("--exclude", multiple=True, metavar="KEY", help="Keys to exclude (repeatable).")
@click.option("--redact-sensitive", is_flag=True, default=False, help="Mask sensitive values.")
@click.option("--redact-mask", default="***", show_default=True, help="Mask string for redaction.")
@click.option("--format", "fmt", type=click.Choice(["dotenv", "json"]), default="dotenv", show_default=True)
@click.option("--summary", "show_summary", is_flag=True, default=False)
def clone_cmd(
    src: str,
    output: str | None,
    include: tuple[str, ...],
    exclude: tuple[str, ...],
    redact_sensitive: bool,
    redact_mask: str,
    fmt: str,
    show_summary: bool,
) -> None:
    """Clone SRC .env file with optional filtering and redaction."""
    env = parse_env_file(Path(src))
    result = clone_env(
        env,
        include=list(include) or None,
        exclude=list(exclude) or None,
        redact_sensitive=redact_sensitive,
        redact_mask=redact_mask,
    )

    if fmt == "json":
        payload = {
            "cloned": result.cloned,
            "redacted_keys": result.redacted_keys,
            "dropped_keys": result.dropped_keys,
            "summary": result.summary(),
        }
        text = json.dumps(payload, indent=2)
    else:
        text = render_cloned(result)

    if output:
        Path(output).write_text(text)
        if show_summary:
            click.echo(result.summary())
    else:
        click.echo(text, nl=False)
        if show_summary:
            click.echo(result.summary(), err=True)

    sys.exit(0)
