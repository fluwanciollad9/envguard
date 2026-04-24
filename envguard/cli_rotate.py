"""CLI command: envguard rotate — rename env keys via a rotation map."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.parser import parse_env_file
from envguard.rotator import rotate_env, render_rotated, summary, was_changed


@click.command("rotate")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--map",
    "rotation_map",
    multiple=True,
    metavar="OLD=NEW",
    required=True,
    help="Key rename pair, e.g. --map OLD_KEY=NEW_KEY. Repeatable.",
)
@click.option("--overwrite-conflicts", is_flag=True, default=False,
              help="Overwrite new_key if it already exists.")
@click.option("--in-place", is_flag=True, default=False,
              help="Write result back to ENV_FILE.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would change without writing.")
@click.option("--format", "fmt", type=click.Choice(["text", "json", "dotenv"]),
              default="dotenv", show_default=True)
def rotate_cmd(
    env_file: str,
    rotation_map: tuple,
    overwrite_conflicts: bool,
    in_place: bool,
    dry_run: bool,
    fmt: str,
) -> None:
    """Rename keys in ENV_FILE according to --map OLD=NEW pairs."""
    rmap: dict = {}
    for pair in rotation_map:
        if "=" not in pair:
            raise click.BadParameter(f"Expected OLD=NEW, got: {pair}", param_hint="--map")
        old, new = pair.split("=", 1)
        rmap[old.strip()] = new.strip()

    env = parse_env_file(env_file)
    result = rotate_env(env, rmap, overwrite_conflicts=overwrite_conflicts)

    if fmt == "json":
        click.echo(json.dumps({
            "rotated": result.rotated,
            "renamed": [list(p) for p in result.renamed],
            "not_found": result.not_found,
            "conflicts": result.conflicts,
            "was_changed": was_changed(result),
        }, indent=2))
    elif fmt == "text":
        click.echo(summary(result))
        for old, new in result.renamed:
            click.echo(f"  {old} -> {new}")
        for key in result.not_found:
            click.echo(f"  NOT FOUND: {key}")
        for key in result.conflicts:
            click.echo(f"  CONFLICT (skipped): {key}")
    else:
        click.echo(render_rotated(result), nl=False)

    if not dry_run and in_place and was_changed(result):
        Path(env_file).write_text(render_rotated(result))
        if fmt != "dotenv":
            click.echo(f"Written to {env_file}")

    if not was_changed(result) and result.not_found:
        sys.exit(1)
