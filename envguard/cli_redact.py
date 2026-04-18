"""CLI command: envguard redact — print env file with secrets masked."""
from __future__ import annotations

import sys
import click

from envguard.parser import parse_env_file
from envguard.redactor import redact_env


@click.command("redact")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--extra-pattern",
    "extra_patterns",
    multiple=True,
    metavar="PATTERN",
    help="Additional key substrings to treat as sensitive (repeatable).",
)
@click.option(
    "--partial",
    is_flag=True,
    default=False,
    help="Show first 4 characters of redacted values instead of full mask.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
)
def redact_cmd(
    env_file: str,
    extra_patterns: tuple[str, ...],
    partial: bool,
    fmt: str,
) -> None:
    """Print ENV_FILE with sensitive values masked."""
    try:
        env = parse_env_file(env_file)
    except OSError as exc:
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(1)

    result = redact_env(env, extra_patterns=list(extra_patterns), show_partial=partial)

    if fmt == "json":
        import json
        payload = {
            "redacted_keys": result.redacted_keys,
            "env": result.redacted,
        }
        click.echo(json.dumps(payload, indent=2))
    else:
        for key, value in result.redacted.items():
            click.echo(f"{key}={value}")
        if result.redacted_keys:
            click.echo(
                f"\n# {len(result.redacted_keys)} key(s) redacted: "
                + ", ".join(result.redacted_keys),
                err=True,
            )
