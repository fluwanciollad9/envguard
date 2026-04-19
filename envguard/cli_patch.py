"""CLI command: envguard patch — apply key=value patches to a .env file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.parser import parse_env_file
from envguard.patcher import patch_env, render_patched


@click.command("patch")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-s",
    "--set",
    "pairs",
    multiple=True,
    metavar="KEY=VALUE",
    help="Key/value pair to patch (repeatable).",
    required=True,
)
@click.option("--in-place", is_flag=True, help="Write changes back to the file.")
@click.option("--dry-run", is_flag=True, help="Show what would change without writing.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
)
def patch_cmd(env_file: str, pairs: tuple, in_place: bool, dry_run: bool, fmt: str) -> None:
    """Patch KEY=VALUE pairs inside ENV_FILE."""
    patches: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid patch format (expected KEY=VALUE): {pair}", err=True)
            sys.exit(1)
        k, _, v = pair.partition("=")
        patches[k.strip()] = v

    env = parse_env_file(Path(env_file))
    result = patch_env(env, patches)

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "applied": [{"key": k, "old": o, "new": n} for k, o, n in result.applied],
                    "not_found": result.not_found,
                    "was_changed": result.was_changed(),
                },
                indent=2,
            )
        )
    else:
        if result.applied:
            for key, old, new in result.applied:
                click.echo(f"  ~ {key}: {old!r} -> {new!r}")
        else:
            click.echo("No changes.")
        if result.not_found:
            click.echo(f"Not found: {', '.join(result.not_found)}", err=True)

    if result.was_changed() and in_place and not dry_run:
        Path(env_file).write_text(render_patched(result))
        click.echo(f"Written to {env_file}")
