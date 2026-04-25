"""CLI command: envguard archive – archive an .env file with a timestamp."""
from __future__ import annotations

import json
from pathlib import Path

import click

from envguard.archiver import archive_env


@click.command("archive")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--dir",
    "archive_dir",
    default=None,
    help="Directory to write the archive into (default: same as ENV_FILE).",
    type=click.Path(file_okay=False),
)
@click.option(
    "--suffix",
    default=".bak",
    show_default=True,
    help="Suffix appended after the timestamp.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
)
def archive_cmd(env_file: str, archive_dir: str | None, suffix: str, fmt: str) -> None:
    """Archive ENV_FILE by copying it with a UTC timestamp in the filename."""
    try:
        result = archive_env(
            Path(env_file),
            archive_dir=Path(archive_dir) if archive_dir else None,
            suffix=suffix,
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "source": str(result.source),
                    "archive_path": str(result.archive_path),
                    "timestamp": result.timestamp,
                    "size_bytes": result.size_bytes,
                    "existed": result.existed,
                },
                indent=2,
            )
        )
    else:
        click.echo(result.summary())
