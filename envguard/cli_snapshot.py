"""CLI commands for snapshot management."""
from __future__ import annotations

import sys
import click

from envguard.snapshotter import diff_with_snapshot, load_snapshot, save_snapshot, take_snapshot
from envguard.reporter import format_diff


@click.group("snapshot")
def snapshot_cmd():
    """Snapshot and compare .env files over time."""


@snapshot_cmd.command("save")
@click.argument("env_file", default=".env")
@click.option("-o", "--output", default=".env.snapshot.json", show_default=True, help="Snapshot output path.")
def save_cmd(env_file: str, output: str):
    """Save a snapshot of ENV_FILE."""
    snap = take_snapshot(env_file)
    save_snapshot(snap, output)
    click.echo(f"Snapshot saved to {output} (timestamp: {snap.timestamp})")


@snapshot_cmd.command("diff")
@click.argument("env_file", default=".env")
@click.option("-s", "--snapshot", "snapshot_path", default=".env.snapshot.json", show_default=True)
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
def diff_cmd(env_file: str, snapshot_path: str, fmt: str):
    """Diff ENV_FILE against a saved snapshot."""
    try:
        result = diff_with_snapshot(env_file, snapshot_path)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    output = format_diff(result, fmt=fmt)
    click.echo(output)
    if result.missing or result.extra or result.changed:
        sys.exit(1)


@snapshot_cmd.command("show")
@click.argument("snapshot_path", default=".env.snapshot.json")
def show_cmd(snapshot_path: str):
    """Show the contents of a saved snapshot."""
    try:
        snap = load_snapshot(snapshot_path)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(f"Source : {snap.source}")
    click.echo(f"Saved  : {snap.timestamp}")
    click.echo(f"Keys   : {len(snap.env)}")
    for key, value in sorted(snap.env.items()):
        click.echo(f"  {key}={value}")
