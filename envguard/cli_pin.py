"""CLI commands for env pinning and drift detection."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envguard.parser import parse_env_file
from envguard.pinner import check_drift, load_lock, pin_env, save_lock


@click.group("pin")
def pin_cmd() -> None:
    """Pin env values and detect drift against a lockfile."""


@pin_cmd.command("lock")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=".env.lock", show_default=True, help="Lock file path")
def lock_cmd(env_file: str, output: str) -> None:
    """Create or update a lock file from ENV_FILE."""
    env = parse_env_file(Path(env_file))
    lock = pin_env(env)
    out = Path(output)
    save_lock(lock, out)
    click.echo(f"Pinned {len(lock)} keys to {out}")


@pin_cmd.command("check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--lock", "-l", "lock_file", default=".env.lock", show_default=True)
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def check_cmd(env_file: str, lock_file: str, fmt: str) -> None:
    """Check ENV_FILE for drift against a lock file."""
    try:
        lock = load_lock(Path(lock_file))
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    env = parse_env_file(Path(env_file))
    result = check_drift(env, lock)

    if fmt == "json":
        click.echo(json.dumps({
            "drifted": result.drifted,
            "new_keys": result.new_keys,
            "removed_keys": result.removed_keys,
            "has_drift": result.has_drift(),
            "summary": result.summary(),
        }, indent=2))
    else:
        click.echo(f"Summary: {result.summary()}")
        if result.drifted:
            click.echo("Drifted: " + ", ".join(result.drifted))
        if result.new_keys:
            click.echo("New:     " + ", ".join(result.new_keys))
        if result.removed_keys:
            click.echo("Removed: " + ", ".join(result.removed_keys))

    sys.exit(1 if result.has_drift() else 0)
