"""CLI commands for tagging env keys."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import click

from .parser import parse_env_file
from .tagger import tag_env, filter_by_tag


def _load_tag_map(tag_map_path: str) -> dict:
    path = Path(tag_map_path)
    if not path.exists():
        click.echo(f"Tag map not found: {tag_map_path}", err=True)
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        click.echo("Tag map must be a JSON object mapping tag -> [keys]", err=True)
        sys.exit(1)
    return data


@click.group("tag")
def tag_cmd():
    """Tag and filter env keys."""


@tag_cmd.command("show")
@click.argument("env_file")
@click.argument("tag_map_file")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def show_cmd(env_file: str, tag_map_file: str, fmt: str):
    """Show tags assigned to each key."""
    env = parse_env_file(env_file)
    tag_map = _load_tag_map(tag_map_file)
    result = tag_env(env, tag_map)

    if fmt == "json":
        click.echo(json.dumps({k: sorted(ts) for k, ts in result.tags.items()}, indent=2))
    else:
        for key, ts in sorted(result.tags.items()):
            label = ", ".join(sorted(ts)) if ts else "(untagged)"
            click.echo(f"{key}: {label}")


@tag_cmd.command("filter")
@click.argument("env_file")
@click.argument("tag_map_file")
@click.argument("tag")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def filter_cmd(env_file: str, tag_map_file: str, tag: str, fmt: str):
    """Print only keys that carry TAG."""
    env = parse_env_file(env_file)
    tag_map = _load_tag_map(tag_map_file)
    result = tag_env(env, tag_map)
    subset = filter_by_tag(env, result, tag)

    if fmt == "json":
        click.echo(json.dumps(subset, indent=2))
    else:
        for k, v in sorted(subset.items()):
            click.echo(f"{k}={v}")

    if not subset:
        sys.exit(1)
