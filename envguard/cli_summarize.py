"""CLI command: envguard summarize — show a high-level report for a .env file."""
from __future__ import annotations

import json
import sys

import click

from envguard.parser import parse_env_file
from envguard.summarizer import summarize_env


@click.command("summarize")
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
    "--passphrase",
    default="",
    help="Passphrase used for audit entropy checks on secrets.",
)
@click.option(
    "--min-score",
    type=float,
    default=None,
    help="Exit non-zero if score is below this threshold.",
)
def summarize_cmd(env_file: str, fmt: str, passphrase: str, min_score: float | None) -> None:
    """Print a high-level summary report for ENV_FILE."""
    env = parse_env_file(env_file)
    report = summarize_env(env, passphrase=passphrase)

    if fmt == "json":
        data = {
            "total_keys": report.total_keys,
            "empty_keys": report.empty_keys,
            "placeholder_keys": report.placeholder_keys,
            "audit_errors": report.audit_errors,
            "audit_warnings": report.audit_warnings,
            "score": report.score,
            "grade": report.grade,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(report.summary())

    if min_score is not None and report.score < min_score:
        sys.exit(1)
